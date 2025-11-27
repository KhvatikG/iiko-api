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


class ProductType(Enum):
    """
    Типы элементов номенклатуры
    """
    GOODS = "GOODS"  # Товар
    DISH = "DISH"  # Блюдо
    PREPARED = "PREPARED"  # Заготовка (полуфабрикат)
    MODIFIER = "MODIFIER"  # Модификатор
    SERVICE = "SERVICE"  # Услуга
    RATE = "RATE"  # Тариф (дочерний элемент для услуги)


class Color(BaseModel):
    """
    Класс для описания цвета
    
    Attributes:
        red: Значение красного канала (0-255)
        green: Значение зеленого канала (0-255)
        blue: Значение синего канала (0-255)
    """
    red: int
    green: int
    blue: int


class Product(BaseModel):
    """
    Класс для описания элемента номенклатуры при импорте
    
    Attributes:
        name: Название элемента номенклатуры (обязательный)
        description: Описание элемента (опциональный)
        parent: ID родительской группы номенклатуры (опциональный)
        modifiers: Список модификаторов (опциональный, пока не используется)
        taxCategory: ID налоговой категории (опциональный)
        category: ID категории (опциональный)
        color: Цвет фона оформления кнопки в iikoFront (опциональный)
        fontColor: Цвет шрифта кнопки в iikoFront (опциональный)
        frontImageId: ID изображения для отображения в iikoFront. API изображений (опциональный)
        position: Позиция в меню (опциональный)
        mainUnit: ID основной единицы измерения (обязательный)
        excludedSections: Множество UUID отделений ресторана, в которых нельзя продавать данный продукт (поле имеет смысл только для блюд) (опциональный)
        defaultSalePrice: Цена продажи по умолчанию (по умолчанию 0)
        placeType: UUID места приготовления блюда (поле имеет смысл только для блюд) (опциональный)
        defaultIncludedInMenu: Включен ли по умолчанию в меню (по умолчанию False)
        type: Тип элемента номенклатуры (обязательный)
        unitWeight: Вес единицы в килограммах (по умолчанию 1)
        unitCapacity: Емкость единицы (по умолчанию 0)
        notInStoreMovement: Не учитывать в движении склада (по умолчанию False)
    """
    name: str
    description: str | None = None
    parent: str | None = None
    modifiers: list | None = None
    taxCategory: str | None = None
    category: str | None = None
    color: Color | None = None
    fontColor: Color | None = None
    frontImageId: str | None = None
    position: int | None = None
    mainUnit: str
    excludedSections: list | None = None
    defaultSalePrice: int | None = None
    placeType: str | None = None
    defaultIncludedInMenu: bool | None = None
    type: ProductType
    unitWeight: float | None = None
    unitCapacity: float | None = None
    notInStoreMovement: bool | None = None


class Order(BaseModel):
    """
    Класс для описания приказа

    Attributes:
        status: Статус приказа, по умолчанию NEW (Сейчас может быть только NEW)
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
