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


class ReferenceType(Enum):
    """
    Типы справочников для работы с API iiko
    
    Используется для получения данных из справочников через эндпоинт /resto/api/v2/entities/list
    """
    MEASURE_UNIT = "MeasureUnit"  # Единицы измерения
    TAX_CATEGORY = "TaxCategory"  # Налоговые категории
    ACCOUNTING_CATEGORY = "AccountingCategory" # Бухгалтерские категории
    PRODUCT_CATEGORY = "ProductCategory" # Пользовательские категории продуктов

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


class ProductWriteoffStrategy(Enum):
    """
    Метод списания технологической карты
    ASSEMBLE - Списывать готовое блюдо
    DIRECT   - Списывать ингредиенты
    """
    ASSEMBLE = "ASSEMBLE"  # Списывать готовое блюдо
    DIRECT = "DIRECT"  # Списывать ингредиенты


class ProductSizeAssemblyStrategy(Enum):
    """
    Стратегия сборки по размерам блюда
    """
    COMMON = "COMMON"  # Общая техкарта для всех размеров
    INDIVIDUAL = "INDIVIDUAL"  # Индивидуальная техкарта для каждого размера


class StoreSpecification(BaseModel):
    """
    Структура для указания подмножества подразделений (департментов),
    в которых действует строка техкарты.
    
    Attributes:
        departments: Список ID подразделений
        inverse: false - фильтр включающий (строка действует для всех перечисленных подразделений),
                 true - фильтр исключающий (строка действует для всех подразделений, КРОМЕ перечисленных)
    """
    departments: list[str] = []
    inverse: bool = False


class AssemblyChartItem(BaseModel):
    """
    Класс для описания ингредиента технологической карты
    
    Attributes:
        sortWeight: Вес сортировки (порядок отображения)
        productId: UUID продукта-ингредиента (обязательный)
        productSizeSpecification: Спецификация размера продукта (опциональный, может быть null или dict)
        storeSpecification: Спецификация склада/подразделения (опциональный)
        amountIn: Количество на входе
        amountMiddle: Количество в процессе (обязательное поле, API не принимает null)
        amountOut: Выход готового продукта в единицах измерения
        amountIn1-3: Акт проработки/Про (опциональные)
        amountOut1-3: Акт проработки/Про (опциональные)
        packageTypeId: UUID фасовки ингредиента (опциональный)
    """
    sortWeight: int = 0
    productId: str
    productSizeSpecification: dict | None = None
    storeSpecification: StoreSpecification | None = None
    amountIn: float = 0.0
    amountMiddle: float = 0.0  # Обязательное поле, API не принимает null
    amountOut: float = 0.0
    amountIn1: float = 0.0
    amountOut1: float = 0.0
    amountIn2: float = 0.0
    amountOut2: float = 0.0
    amountIn3: float = 0.0
    amountOut3: float = 0.0
    packageTypeId: str | None = None


class AssemblyChart(BaseModel):
    """
    Класс для описания технологической карты при сохранении
    
    Attributes:
        assembledProductId: UUID продукта, для которого создается техкарта (обязательный)
        dateFrom: Дата начала действия техкарты в формате "yyyy-MM-dd" (обязательный)
        dateTo: Дата окончания действия техкарты в формате "yyyy-MM-dd" (опциональный, null - без ограничения)
        assembledAmount: Количество готового продукта
        productWriteoffStrategy: Метод списания (ASSEMBLE - списывать готовое блюдо, DIRECT - списывать ингредиенты)
        effectiveDirectWriteoffStoreSpecification: Спецификация подразделений для прямого списания
        productSizeAssemblyStrategy: Стратегия сборки по размерам (COMMON - общая, INDIVIDUAL - индивидуальная)
        items: Список ингредиентов техкарты
        technologyDescription: Комментарий "Технология приготовления"
        description: Комментарий "Описание"
        appearance: Комментарий "Требования к оформлению и реализации"
        organoleptic: Комментарий "Органолептические показатели качества"
        outputComment: Суммарный выход
    """
    assembledProductId: str
    dateFrom: str
    dateTo: str | None = None
    assembledAmount: float
    productWriteoffStrategy: ProductWriteoffStrategy
    effectiveDirectWriteoffStoreSpecification: StoreSpecification
    productSizeAssemblyStrategy: ProductSizeAssemblyStrategy
    items: list[AssemblyChartItem]
    technologyDescription: str = ""
    description: str = ""
    appearance: str = ""
    organoleptic: str = ""
    outputComment: str = ""