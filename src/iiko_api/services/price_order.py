from ..models.models import Item, Order


class IikoPriceOrderService:
    """
    Класс для работы с сервисом формирования приказа
    """
    def __init__(self, iiko_api):
        """
        Конструктор

        :param iiko_api: Объект класса IikoApi
        """
        self.iiko_api = iiko_api

    def set_price(self, dishes: list[Item], order_date: str):
        """
        Формируем приказ для заведения department_id, со списком блюд dishes, с датой order_date

        :param order_date: Дата приказа вида "2024-12-23"
        :param dishes: Список блюд (в поле price должна быть указана новая цена) (см. models/Item)
        :return: None
        """

        # Создаем приказ
        order = Order(dateIncoming=order_date, items=dishes)

        self.iiko_api.orders.set_new_order(order)
