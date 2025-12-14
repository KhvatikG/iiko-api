import json

from requests import Response

from iiko_api.core import BaseClient
from iiko_api.models.models import ReferenceType


class ReferencesEndpoints:
    """
    Класс предоставляющий методы для работы со справочниками
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_entities(self, root_type: str) -> list[dict]:
        """
        Получение списка элементов справочника по типу

        :param root_type: Тип справочника (например, "MeasureUnit", "TaxCategory", "AccountingCategory", "ProductCategory")
        :return: Список словарей, где каждый словарь представляет элемент справочника
        :raises ValueError: если root_type пустой или ответ API не является валидным JSON
        """
        if not root_type:
            raise ValueError("root_type не может быть пустым")

        url = "/resto/api/v2/entities/list"
        params = {"rootType": root_type}

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.get(url, params=params)

        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e

    def get_measure_units(self) -> list[dict]:
        """
        Получение списка единиц измерения

        :return: Список словарей, где каждый словарь представляет единицу измерения
        :raises ValueError: если ответ API не является валидным JSON
        """
        return self.get_entities(ReferenceType.MEASURE_UNIT.value)

    def get_tax_categories(self) -> list[dict]:
        """
        Получение списка налоговых категорий

        :return: Список словарей, где каждый словарь представляет налоговую категорию
        :raises ValueError: если ответ API не является валидным JSON
        """
        return self.get_entities(ReferenceType.TAX_CATEGORY.value)

    def get_accounting_categories(self) -> list[dict]:
        """
        Получение списка бухгалтерских категорий

        :return: Список словарей, где каждый словарь представляет бухгалтерскую категорию
        :raises ValueError: если ответ API не является валидным JSON
        """
        return self.get_entities(ReferenceType.ACCOUNTING_CATEGORY.value)

    def get_product_categories(self) -> list[dict]:
        """
        Получение списка пользовательских категорий продуктов

        :return: Список словарей, где каждый словарь представляет категорию продукта
        :raises ValueError: если ответ API не является валидным JSON
        """
        return self.get_entities(ReferenceType.PRODUCT_CATEGORY.value)

