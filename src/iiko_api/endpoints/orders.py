from requests import Response
from ..models.models import Order


class OrdersEndpoints:
    """
    Эндпоинты для работы с приказами
    """
    def __init__(self, client):
        self.client = client

    def set_new_order(self, order: Order):
        """
        Создание нового приказа
        :return:
        """
        # Авторизация
        self.client.login()

        url = "/resto/api/v2/documents/menuChange"

        result: Response = self.client.post(endpoint=url, data=order.model_dump_json())
        print("-----------ПРИКАЗ ОТПРАВЛЕН НА СЕРВЕР----------------------")
        print(str(result))
        print(result.status_code)
        print(result.text)
        print(result.json())

        # Отпускаем авторизацию
        self.client.logout()

