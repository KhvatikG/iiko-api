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

    def get_price_list(self, date_from: str, date_to: str = None, department_id: str = None) -> dict | None:
        """
        Получение цен устаовленных приказами

        :param date_from: Начало временного интервала в формате "yyyy-MM-dd". Обязательный.
        :param date_to: Конец временного интервала в формате "yyyy-MM-dd".
                        По умолчанию server iiko установит'2500-01-01'.
        :param department_id: Список ресторанов, по которым делается запрос. Если не задан, то для всех.
        :return:
        """

        url = "/resto/api/v2/price?"
        if not date_from:
            raise Exception("Не задан параметр date_from")
        else:
            url += f"dateFrom={date_from}&"

        if date_to:
            url += f"dateTo={date_to}&"

        if department_id:
            if isinstance(department_id, list):
                url += f"departmentId={department_id[0]}"
                for i in department_id[1:]:
                    url += f"&departmentId={i}"
            else:
                url += f"departmentId={department_id}"

        # Авторизация
        self.client.login()

        result: Response = self.client.get(endpoint=url)

        # Отпускаем авторизацию
        self.client.logout()

        if result.status_code == 200:
            return result.json()
        else:
            return None
