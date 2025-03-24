from requests import Response

from iiko_api.core import BaseClient


class DishesEndpoints:
    """
    Класс предоставляющий методы для работы с номенклатурой
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_nomenclature_list(self,
                              articles: list[str] | None = None,
                              ids: list[str] | None = None,
                              types: list[str] | None = None,
                              include_deleted: bool = False,
                              ) -> list[dict] | None:
        """
        Получение списка элементов номенклатуры, по артикулу, по id и по типу элемента номенклатуры.

        :param include_deleted: включать ли удаленные элементы номенклатуры
        :param types: список типов элементов номенклатуры,
         по которым необходимо получить список элементов номенклатуры, если None - получить все
        :param articles: список артикулов, по которым необходимо получить список элементов, если None - получить все
        :param ids: список id, по которым необходимо получить список, если None - получить все
        :return: список словарей, где каждый словарь представляет элемент номенклатуры
        """
        url = "/resto/api/v2/entities/products/list"
        url += "?"

        if include_deleted:
            url += "includeDeleted=true&"

        if articles:
            for article in articles:
                url += f"nums={article}&"
        if ids:
            for id_ in ids:
                url += f"ids={id_}&"
        if types:
            for type_ in types:
                url += f"types={type_}&"

        # Авторизация
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные об элементах номенклатуры
        result: Response = self.client.get(url)

        # Отпускаем авторизацию
        self.client.logout()

        if result.status_code == 200:
            return result.json()
        else:
            return None

    def get_nomenclature_groups(
            self, ids: list[str] | None = None,
            parent_ids: list[str] | None = None,
            nums: list[str] | None = None,
            include_deleted: bool = False,
    ) -> list[dict] | None:
        """
        Получение списка групп номенклатуры

        :param include_deleted: включать ли удаленные группы номенклатуры
        :param ids: список id групп номенклатуры, по которым необходимо получить список, если None - получить все
        :param parent_ids: список id родительских групп номенклатуры, по которым необходимо получить список,
         если None - получить все
        :param nums: список артикулов групп номенклатуры, по которым необходимо получить список,
         если None - получить все

        :return: список словарей, где каждый словарь представляет группу номенклатуры
        """
        url = "/resto/api/v2/entities/products/group/list"
        url += "?"

        if ids:
            for id_ in ids:
                url += f"ids={id_}&"

        if parent_ids:
            for parent_id in parent_ids:
                url += f"parentIds={parent_id}&"

        if nums:
            for num in nums:
                url += f"nums={num}&"

        if include_deleted:
            url += "includeDeleted=true"

        # Авторизация
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные об элементах номенклатуры
        result: Response = self.client.get(url)

        # Отпускаем авторизацию
        self.client.logout()

        if result.status_code == 200:
            return result.json()
        else:
            return
