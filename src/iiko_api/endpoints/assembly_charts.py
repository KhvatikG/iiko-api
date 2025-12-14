import json
import re
from typing import Any

from requests import Response

from iiko_api.core import BaseClient
from iiko_api.exceptions import IikoAPIError
from iiko_api.models.models import AssemblyChart


class AssemblyChartsEndpoints:
    """
    Класс, предоставляющий методы для работы с техкартами.
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_all_assembly_charts(
            self,
            date_from: str,
            date_to: str = None,
            include_prepared_charts: bool = True,
            include_deleted_products: bool = False
    ) -> dict:
        """
        Получение всех техкарт.

        :param date_from: Дата начала периода в формате "yyyy-MM-dd"
        :param date_to: Дата окончания периода в формате "yyyy-MM-dd" (необязательный параметр)
        :param include_prepared_charts: Разложить ли вложенные техкарты до конечных ингредиентов (по умолчанию True)
        :param include_deleted_products: Включать ли техкарты с удаленными продуктами (по умолчанию False)
        :return: Словарь с ключами:
            - assemblyCharts: Список исходных технологических карт,
              интервал действия которых пересекает запрошенный интервал
            - preparedCharts: Список разложенных до ингредиентов технологических карт,
              интервал действия которых пересекает запрошенный интервал
        :raises ValueError: если date_from имеет неверный формат или ответ API не является валидным JSON
        """
        if not date_from:
            raise ValueError("date_from не может быть пустым")
        
        # Валидация формата даты (только yyyy-MM-dd)
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, date_from):
            raise ValueError(
                f"date_from должен быть в формате 'yyyy-MM-dd', получено: '{date_from}'"
            )
        
        if date_to and not re.match(date_pattern, date_to):
            raise ValueError(
                f"date_to должен быть в формате 'yyyy-MM-dd', получено: '{date_to}'"
            )

        url = "/resto/api/v2/assemblyCharts/getAll"
        params: dict[str, Any] = {
            "dateFrom": date_from,
            "includePreparedCharts": include_prepared_charts,
            "includeDeletedProducts": include_deleted_products
        }
        
        if date_to:
            params["dateTo"] = date_to

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.get(url, params=params)

        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e

    def save_assembly_chart(self, assembly_chart: AssemblyChart) -> dict:
        """
        Сохранение технологической карты.
        
        :param assembly_chart: Объект AssemblyChart с данными технологической карты
        :return: Словарь с полной технологической картой, созданной на сервере.
                 Возвращаемая техкарта содержит все поля из запроса плюс дополнительные поля от сервера:
                 - id: UUID созданной техкарты
                 - items[].id: UUID созданных ингредиентов
                 - items[].packageCount: количество фасовок (если применимо)
                 и другие поля, возвращаемые API
        :raises IikoAPIError: если API вернул ошибку (result != SUCCESS или неожиданный формат ответа)
        :raises ValueError: если ответ API не является валидным JSON
        """
        url = "/resto/api/v2/assemblyCharts/save"
        headers = {"Content-Type": "application/json"}
        
        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.post(
            endpoint=url,
            data=assembly_chart.model_dump_json(exclude_none=True),
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
        # response содержит полную созданную техкарту со всеми полями от сервера
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
            error_message = "Ошибка при сохранении техкарты"
            if error_messages:
                error_message += f". Ошибки: {', '.join(error_messages)}"
            else:
                error_message += f". Статус: {result_status}"
            
            raise IikoAPIError(error_message, errors=errors)
        else:
            # Неожиданный статус (не SUCCESS и не ERROR)
            raise IikoAPIError(
                f"API вернул неожиданный статус результата: {result_status}. "
                f"Полный ответ: {response_data}"
            )
