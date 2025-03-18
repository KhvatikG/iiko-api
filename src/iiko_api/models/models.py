from enum import Enum
from pydantic import BaseModel


class Item(BaseModel):
    """
    Класс для хранения данных об элементе номенклатуры

    Attributes:
        departmentId: идентификатор отдела (обязательный)
        productId: идентификатор продукта (обязательный)
        including: включен ли продукт в приказ по умолчанию True
        price: цена продукта (обязательный)
        flyerProgram: включен ли продукт в программу "Флаер" - по умолчанию False
        dishOfDay: включен ли продукт в "Блюдо дня" - по умолчанию False
    """
    departmentId: str
    productId: str
    including: bool = True
    price: int
    flyerProgram: bool = False
    dishOfDay: bool = False


class Status(Enum):
    """
    Статус приказа
    Пока кроме NEW ничего не используется
    """
    NEW = 'NEW'


class Order(BaseModel):
    """
    Класс для описания приказа

    Attributes:
        status: Статус приказа, по умолчанию NEW
        dateIncoming: Дата приказа вида "2024-12-23" (обязательно)
        shortName: Короткое название приказа
        deletePreviousMenu: Удалять ли предыдущее меню(ДОЛЖНО БЫТЬ FALSE!)
        items: Список блюд
    """
    status: Status = Status.NEW
    dateIncoming: str
    shortName: str = ""
    deletePreviousMenu: bool = False
    items: list[Item] | list[None] = []
