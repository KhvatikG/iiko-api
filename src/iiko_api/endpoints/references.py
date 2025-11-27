from requests import Response

from iiko_api.core import BaseClient
from iiko_api.models.models import ReferenceType


class ReferencesEndpoints:
    """
    Класс предоставляющий методы для работы со справочниками
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_entities(self, root_type: str) -> list[dict] | None:
        """
        Получение списка элементов справочника по типу

        :param root_type: Тип справочника (например, "MeasureUnit", "TaxCategory")
        :return: Список словарей, где каждый словарь представляет элемент справочника, или None в случае ошибки
        """
        url = "/resto/api/v2/entities/list"
        params = {"rootType": root_type}

        # Выполнение GET-запроса к API, возвращающего данные справочника
        result: Response = self.client.get(url, params=params)

        if result.status_code == 200:
            return result.json()
        else:
            return None

    def get_measure_units(self) -> list[dict] | None:
        """
        Получение списка единиц измерения

        :return: Список словарей, где каждый словарь представляет единицу измерения, или None в случае ошибки
        """
        return self.get_entities(ReferenceType.MEASURE_UNIT.value)

    def get_tax_categories(self) -> list[dict] | None:
        """
        Получение списка налоговых категорий

        :return: Список словарей, где каждый словарь представляет налоговую категорию, или None в случае ошибки
        """
        return self.get_entities(ReferenceType.TAX_CATEGORY.value)

