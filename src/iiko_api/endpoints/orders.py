import json
from requests import Response
from typing import Any

from iiko_api.core import BaseClient
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

        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e

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
