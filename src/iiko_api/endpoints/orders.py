import json
from typing import Any

from requests import Response

from iiko_api.core import BaseClient
from iiko_api.exceptions import IikoAPIError

from ..models.models import Order


class OrdersEndpoints:
    """
    Эндпоинты для работы с приказами
    """
    def __init__(self, client: BaseClient):
        self.client = client

    def set_new_order(self, order: Order) -> dict:
        """
        Создание нового приказа

        :param order: Объект Order с данными приказа
        :return: словарь с результатом создания приказа
        :raises IikoAPIError: если API вернул ошибку (result != SUCCESS или неожиданный формат ответа)
        :raises ValueError: если ответ API не является валидным JSON
        """
        url = "/resto/api/v2/documents/menuChange"
        headers = {"Content-Type": "application/json"}

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.post(
            endpoint=url,
            data=order.model_dump_json(),
            headers=headers
        )

        # Безопасный парсинг JSON ответа
        try:
            response_data = result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e

        # Проверяем, что ответ - словарь (не список и не строка)
        if not isinstance(response_data, dict):
            raise IikoAPIError(
                f"API вернул неожиданный формат ответа (ожидался dict, получен {type(response_data).__name__}): {response_data}"
            )

        # API возвращает структуру с полями result, errors, response
        # response содержит результат создания приказа
        result_status = response_data.get("result")

        if result_status == "SUCCESS":
            response_result = response_data.get("response")
            if response_result is None:
                # Если response отсутствует, возвращаем весь ответ
                return response_data
            return response_result
        elif result_status == "ERROR":
            # Бизнес-ошибка API: HTTP 200, но операция не выполнена
            errors = response_data.get("errors", [])
            # Безопасная обработка errors - может быть не списком
            if not isinstance(errors, list):
                errors = []

            error_messages = [
                f"{err.get('code', 'UNKNOWN')}: {err.get('value', '')}"
                for err in errors
                if isinstance(err, dict)
            ]
            error_message = "Ошибка при создании приказа"
            if error_messages:
                error_message += f". Ошибки: {', '.join(error_messages)}"
            else:
                error_message += f". Статус: {result_status}"

            raise IikoAPIError(error_message, errors=errors)
        else:
            # Неожиданный статус (не SUCCESS и не ERROR) или None
            raise IikoAPIError(
                f"API вернул неожиданный статус результата: {result_status}. "
                f"Полный ответ: {response_data}"
            )

    def get_price_list(
            self,
            date_from: str,
            date_to: str = None,
            type_: str = "BASE",
            department_id: str | list = None
    ) -> dict:
        """
        Получение цен установленных приказами

        :param date_from: Начало временного интервала в формате "yyyy-MM-dd". Обязательный.
        :param date_to: Конец временного интервала в формате "yyyy-MM-dd".
                        По умолчанию server iiko установит '2500-01-01'.
        :param type_: Цены какого типа выгружать. Если None, то все. Типы:
            BASE - Цена, которая действует на всем заданном интервале, т.е. из базового приказа.
            SCHEDULED - Цена, которая действует по расписанию на заданном интервале, т.е. из приказа по времени.
        :param department_id: Список ресторанов, по которым делается запрос. Если не задан, то для всех.
        :return: словарь с данными о ценах
        :raises ValueError: если date_from не задан или ответ API не является валидным JSON
        """

        if not date_from:
            raise ValueError("Не задан параметр date_from")

        url = "/resto/api/v2/price"
        params: dict[str, Any] = {
            "dateFrom": date_from
        }

        if date_to:
            params["dateTo"] = date_to

        if type_ in ("BASE", "SCHEDULED"):
            params["type"] = type_

        if department_id:
            if isinstance(department_id, list):
                # Для списка добавляем несколько параметров departmentId
                params["departmentId"] = department_id
            else:
                params["departmentId"] = department_id

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.get(endpoint=url, params=params)

        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e
