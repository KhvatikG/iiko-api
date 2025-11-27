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
        url = "/resto/api/v2/documents/menuChange"
        header = {"Content-Type": "application/json"}

        result: Response = self.client.post(endpoint=url, data=order.model_dump_json(), headers=header)

    def get_price_list(
            self,
            date_from: str,
            date_to: str = None,
            type_: str = "BASE",
            department_id: str | list = None
    ) -> dict | None:
        """
        Получение цен установленных приказами

        :param date_from: Начало временного интервала в формате "yyyy-MM-dd". Обязательный.
        :param date_to: Конец временного интервала в формате "yyyy-MM-dd".
                        По умолчанию server iiko установит'2500-01-01'.
        :param type_: Цены какого типа выгружать. Если None, то все. Типы:
            BASE - Цена, которая действует на всем заданном интервале, т.е. из базового приказа.
            SCHEDULED - Цена, которая действует по расписанию на заданном интервале, т.е. из приказа по времени.
        :param department_id: Список ресторанов, по которым делается запрос. Если не задан, то для всех.
        :return:
        """

        url = "/resto/api/v2/price?"

        match type_:
            case "BASE":
                url += "type=BASE&"
            case "SCHEDULED":
                url += "type=SCHEDULED&"
            case _:
                pass

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

        result: Response = self.client.get(endpoint=url)

        if result.status_code == 200:
            return result.json()
        else:
            return None
