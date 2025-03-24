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
