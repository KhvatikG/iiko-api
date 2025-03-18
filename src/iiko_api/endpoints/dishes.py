from iiko_api.core import BaseClient


class DishesEndpoints:
    """
    Класс предоставляющий методы для работы с номенклатурой
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_dishes(self, articles: list[str] | None = None):
        """
        Получение списка блюд
        :param articles: список артикулов, по которым необходимо получить список блюд, если None - получить все блюда
        :return: список словарей, где каждый словарь представляет блюдо
        """
        url = "/resto/api/v2/entities/products/list"
        if articles:
            url += "?"
            for article in articles:
                url += f"nums={article}&"

        # Авторизация
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные о блюдах
        json_data = self.client.get(url)

        # Отпускаем авторизацию
        self.client.logout()

        return json_data.json()
