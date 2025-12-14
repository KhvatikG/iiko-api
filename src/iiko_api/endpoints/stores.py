import json
import re
from datetime import datetime
from typing import Any

import xmltodict
from requests import Response

from iiko_api.core import BaseClient


class StoresEndpoints:
    """
    Класс, предоставляющий методы для работы со складами
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_stores(self, auto_login=True) -> list[dict]:
        """
        Метод для получения списка складов

        :param auto_login: Параметр оставлен для обратной совместимости, но больше не используется
        :return: Список словарей, где каждый словарь представляет склад
        :raises ValueError: если XML не может быть распарсен или структура данных неожиданная
        """
        url = "/resto/api/corporation/stores"

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        xml_data = self.client.get(url)

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        # Безопасное извлечение данных из структуры XML
        try:
            corporate_items = dict_data.get("corporateItemDtoes", {})
            stores = corporate_items.get("corporateItemDto")
            
            # Если stores - None или пустой словарь, возвращаем пустой список
            if stores is None:
                return []
            
            # Если stores - один элемент (не список), преобразуем в список
            if isinstance(stores, dict):
                return [stores]
            
            # Если stores - список, возвращаем как есть
            if isinstance(stores, list):
                return stores
            
            raise ValueError(f"Неожиданная структура данных: {type(stores)}")
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура corporateItemDtoes/corporateItemDto. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e

    def get_stores_balance(self, timestamp: str = "now", auto_login=True) -> dict:
        """
        Метод для получения остатков на складах

        :param auto_login: Параметр оставлен для обратной совместимости, но больше не используется
        :param timestamp: Дата, на которую необходимо получить остатки в формате "yyyy-MM-dd".
                         Если указано "now", используется текущая дата в формате "yyyy-MM-dd"
        :return: Словарь с данными об остатках на складах
        :raises ValueError: если timestamp имеет неверный формат или ответ API не является валидным JSON
        """
        url = "/resto/api/v2/reports/balance/stores"

        # Определяем значение timestamp
        if timestamp == "now":
            timestamp_value = datetime.now().strftime('%Y-%m-%d')
        else:
            # Валидация формата даты (только yyyy-MM-dd)
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, timestamp):
                raise ValueError(
                    f"timestamp должен быть в формате 'yyyy-MM-dd' или 'now', получено: '{timestamp}'"
                )
            timestamp_value = timestamp

        params: dict[str, Any] = {"timestamp": timestamp_value}

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.get(url, params=params)

        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e
