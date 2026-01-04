# iiko-api

**Версия:** 1.0.0

Библиотека для работы с API iiko.

## Содержание

- [Описание](#описание)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [Аутентификация](#аутентификация)
- [Эндпоинты и методы](#эндпоинты-и-методы)
  - [IikoApi.employees](#iikoapiemployees---эндпоинты-для-работы-с-сотрудниками)
  - [IikoApi.roles](#iikoapiroles---эндпоинты-для-работы-с-ролями)
  - [IikoApi.reports](#iikoapireports---отчеты)
  - [IikoApi.nomenclature](#iikoapinomenclature---номенклатура)
  - [IikoApi.orders](#iikoapiorders---приказы)
  - [IikoApi.assembly_charts](#iikoapiassembly_charts---тех-карты)
  - [IikoApi.stores](#iikoapistores---склады)
  - [IikoApi.olap](#iikoapiolap---olap-отчеты)
  - [IikoApi.references](#iikoapireferences---справочники)
- [Модели данных](#модели-данных)
- [Сервисы](#сервисы)
- [Обработка исключений](#обработка-исключений)
- [Параметры инициализации](#параметры-инициализации)

## Описание

Библиотека предоставляет базовый класс `IikoApi` для работы с API iiko. 
Этот класс предоставляет методы для выполнения GET и POST запросов к API, 
а также методы для аутентификации и отмены аутентификации.

## Требования

- Python >=3.10

### Зависимости

- pydantic>=2.10.6
- python-dotenv>=1.0.1
- requests>=2.32.3
- xmltodict>=0.14.2

## Установка
### Используя uv
Добавьте в pyproject.toml:
```toml
[tool.uv.sources]
iiko-api = { git = "https://github.com/KhvatikG/iiko-api.git" }
```
И выполните 

```bash
uv add iiko-api
```

## Использование

```python
from iiko_api import IikoApi
from dotenv import dotenv_values

# Если используем .env подгружаем из него данные для конфигурации
config = dotenv_values(".env")

iiko_client = IikoApi(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS")
)

# Получение списка всех сотрудников (требует аутентификации)
with iiko_client.auth_context():
    employees = iiko_client.employees.get_employees()

# Получение списка всех ролей (требует аутентификации)
with iiko_client.auth_context():
    roles = iiko_client.roles.get_roles()
```
## Аутентификация

**Важно:** Аутентификация в библиотеке НЕ выполняется автоматически. Для выполнения запросов, требующих авторизации, необходимо использовать контекстный менеджер или декоратор.

`IikoApi` предоставляет контекстный менеджер для авторизованного выполнения блока кода и декоратор:
```python
from iiko_api import IikoApi
from dotenv import dotenv_values

# Если используем .env подгружаем из него данные для конфигурации
config = dotenv_values(".env")

iiko_client = IikoApi(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS")
)

# Аутентификация через декоратор
@iiko_client.with_authorization
def my_function():
    """Несколько обращений к iiko с использованием IikoApi get | post"""
    iiko_client.client.get('/resto/api/employees/')
    iiko_client.client.post(...)

# Аутентификация через контекстный менеджер
with iiko_client.auth_context():
  iiko_client.client.get('/resto/api/employees/')
  iiko_client.client.post(...)
```
В представленном примере все обращения в рамках функции или контекстного менеджера будут выполнены в рамках одной авторизованной сессии.
Методы `client.get` и `client.post` уже содержат `BASE_URL` и ожидают только конечную точку.
`post` также может принимать заголовки и тело:
`post(endpoint: str, data: dict[str, Any] = None, headers: dict[str, Any] = None)`



## Эндпоинты и методы

**Примечание:** Методы в этом разделе требуют аутентификации. Используйте контекстный менеджер `auth_context()` или декоратор `with_authorization` для выполнения запросов, требующих авторизации.

### IikoApi.employees - Эндпоинты для работы с сотрудниками
- `get_employees() -> list[dict]` - Возвращает всех сотрудников в виде списка словарей.
- `get_employee_by_id(employee_id: UUID) -> dict` - Возвращает сотрудника по id. Параметр `employee_id` может быть объектом `UUID` из модуля `uuid` или строкой, содержащей UUID.
- `get_employees_by_department(department_code: str) -> list[dict]` - Возвращает сотрудников определенного отдела по его коду.
- `get_attendances_for_department(department_code: str, date_from: datetime, date_to: datetime) -> list[dict]` - Возвращает список явок сотрудников для отдела за период.

### IikoApi.roles - Эндпоинты для работы с ролями
- `get_roles() -> list[dict]` - Возвращает список всех ролей.
- `get_role_by_id(role_id: str) -> dict` - Возвращает роль по её id.

### IikoApi.reports - Отчеты
- `get_sales_report(date_from: datetime, date_to: datetime, department_id: str, date_aggregation: bool = True) -> dict[date, float] | list[dict]`
    Получение отчета по продажам за период.
    Возвращает словарь, где ключ это дата, а значение это выручка, если `date_aggregation=True`.
    Если `date_aggregation=False`, то отчет будет списком словарей с ключами `date` и `value`.

### IikoApi.nomenclature - Номенклатура

- `get_nomenclature_list(nums: list[str] | None = None, ids: list[str] | None = None, types: list[str] | None = None, category_ids: list[str] | None = None, parent_ids: list[str] | None = None, include_deleted: bool = False) -> list[dict]`
    Получение списка элементов номенклатуры с фильтрацией по артикулу (`nums`), по id, по типу элемента номенклатуры, по категории продукта и по родительской группе.
    Возвращает список словарей, где каждый словарь представляет элемент номенклатуры.

- `get_nomenclature_groups(ids: list[str] | None = None, parent_ids: list[str] | None = None, nums: list[str] | None = None, include_deleted: bool = False) -> list[dict]`
    Получение списка групп номенклатуры с фильтрами по id, id родительской категории, артикулу.
    Возвращает список словарей, где каждый словарь представляет группу номенклатуры.

- `import_product(product: Product) -> dict`
    Импорт элемента номенклатуры в iiko.
    Принимает объект `Product` из `iiko_api.models` и возвращает словарь с результатом импорта (содержит созданный продукт).
    Вызывает `IikoAPIError` при ошибке API (result != SUCCESS).

### IikoApi.orders - Приказы
- `set_new_order(order: Order) -> dict`
    Создание нового приказа в iiko.
    Приказ необходимо создать используя классы из `iiko_api.models`.
    
    Пример использования:
    ```python
    from iiko_api.models import Order, Item, Status
    
    # Создание элементов приказа
    items = [
        Item(
            departmentId="uuid-отдела",
            productId="uuid-продукта",
            price=1000,
            including=True
        )
    ]
    
    # Создание приказа
    order = Order(
        status=Status.NEW,
        dateIncoming="2024-12-23",
        shortName="Приказ на декабрь",
        deletePreviousMenu=False,
        items=items
    )
    
    # Отправка приказа (требует аутентификации)
    with iiko_client.auth_context():
        result = iiko_client.orders.set_new_order(order)
    ```

- `get_price_list(date_from: str, date_to: str = None, type_: str = "BASE", department_id: str | list = None) -> dict`
    Получение цен установленных приказами.
    - `date_from` - Начало временного интервала в формате "yyyy-MM-dd" (обязательный).
    - `date_to` - Конец временного интервала в формате "yyyy-MM-dd" (по умолчанию server iiko установит '2500-01-01').
    - `type_` - Тип цены для выгрузки: `"BASE"` (цена на всем интервале) или `"SCHEDULED"` (цена по расписанию).
    - `department_id` - Список ресторанов, по которым делается запрос. Если не задан, то для всех.

### IikoApi.assembly_charts - Тех карты
- `get_all_assembly_charts(date_from: str, date_to: str = None, include_prepared_charts: bool = True, include_deleted_products: bool = False) -> dict`
    Получение всех техкарт.
    - `date_from` - Дата начала периода в формате "yyyy-MM-dd".
    - `date_to` - Дата окончания периода в формате "yyyy-MM-dd" (необязательный параметр).
    - `include_prepared_charts` - Разложить ли вложенные техкарты до конечных ингредиентов (по умолчанию True).
    - `include_deleted_products` - Включать ли техкарты с удаленными продуктами (по умолчанию False).
    
    Возвращает словарь с ключами:
    - `assemblyCharts` - Список исходных технологических карт, интервал действия которых пересекает запрошенный интервал.
    - `preparedCharts` - Список разложенных до ингредиентов технологических карт, интервал действия которых пересекает запрошенный интервал.

- `save_assembly_chart(assembly_chart: AssemblyChart) -> dict`
    Сохранение технологической карты в iiko.
    Принимает объект `AssemblyChart` из `iiko_api.models` и возвращает словарь с полной технологической картой, созданной на сервере (содержит все поля из запроса плюс дополнительные поля от сервера: id, items[].id и др.).
    Вызывает `IikoAPIError` при ошибке API (result != SUCCESS).

### IikoApi.stores - Склады
- `get_stores(auto_login=True) -> list[dict]`
    Получение списка складов.
    Параметр `auto_login` оставлен для обратной совместимости, но больше не используется.

- `get_stores_balance(timestamp: str = "now", auto_login=True) -> dict`
    Получение остатков на складах.
    - `timestamp` - Дата, на которую необходимо получить остатки в формате "yyyy-MM-dd", если "now" то используется текущая дата.
    - `auto_login` - Параметр оставлен для обратной совместимости, но больше не используется.

### IikoApi.olap - OLAP отчеты
- `get_olap_by_preset_id(preset_id: str, date_from: datetime = None, date_to: datetime = None, auto_login: bool = True) -> dict`
    Получение отчета по ID преднастроенного отчета.
    - `preset_id` - UUID пресета в iiko (можно получить по /resto/api/v2/reports/olap/presets).
    - `date_from` - Дата начала отчета (включается в отчет).
    - `date_to` - Дата конца отчета (не включается в отчет и должна быть больше чем date_from).
    - `auto_login` - Параметр оставлен для обратной совместимости, но больше не используется.
    
    Дата начала и конца отчета должны отличаться.

### IikoApi.references - Справочники
- get_entities(root_type: str) -> list[dict]
    Получение списка элементов справочника по типу.
    `root_type` - Тип справочника (например, "MeasureUnit", "TaxCategory", "AccountingCategory", "ProductCategory").
    Можно использовать значения из enum `ReferenceType` из `iiko_api.models`.

- get_measure_units() -> list[dict]
    Получение списка единиц измерения.
    Удобный метод для получения единиц измерения (эквивалент `get_entities(ReferenceType.MEASURE_UNIT.value)`).

- get_tax_categories() -> list[dict]
    Получение списка налоговых категорий.
    Удобный метод для получения налоговых категорий (эквивалент `get_entities(ReferenceType.TAX_CATEGORY.value)`).

- get_accounting_categories() -> list[dict]
    Получение списка бухгалтерских категорий.
    Удобный метод для получения бухгалтерских категорий (эквивалент `get_entities(ReferenceType.ACCOUNTING_CATEGORY.value)`).

- get_product_categories() -> list[dict]
    Получение списка пользовательских категорий продуктов.
    Удобный метод для получения категорий продуктов (эквивалент `get_entities(ReferenceType.PRODUCT_CATEGORY.value)`).

## Модели данных

Библиотека предоставляет модели данных на основе Pydantic для работы с API iiko. Все модели находятся в модуле `iiko_api.models`.

### Основные модели

#### `Order`
Класс для описания приказа:
```python
from iiko_api.models import Order, Item, Status

# Создание элементов приказа
items = [
    Item(
        departmentId="uuid-отдела",
        productId="uuid-продукта",
        price=1000
    )
]

# Создание приказа
order = Order(
    status=Status.NEW,
    dateIncoming="2024-12-23",
    shortName="Приказ на декабрь",
    deletePreviousMenu=False,
    items=items
)
```

**Атрибуты:**
- `status: Status` - Статус приказа, по умолчанию `Status.NEW` (сейчас может быть только NEW)
- `dateIncoming: str` - Дата приказа в формате "yyyy-MM-dd" (обязательный)
- `shortName: str` - Короткое название приказа (по умолчанию "")
- `deletePreviousMenu: bool` - Удалять ли предыдущее меню (ДОЛЖНО БЫТЬ False!)
- `items: list[Item]` - Список блюд

#### `Item`
Класс для хранения данных об элементе номенклатуры в приказе:
```python
from iiko_api.models import Item

item = Item(
    departmentId="uuid-отдела",
    productId="uuid-продукта",
    including=True,
    price=1000,
    flyerProgram=False,
    dishOfDay=False
)
```

**Атрибуты:**
- `departmentId: str` - Идентификатор отдела (обязательный)
- `productId: str` - Идентификатор продукта (обязательный)
- `including: bool` - Включен ли продукт в приказ (по умолчанию True)
- `price: int` - Цена продукта (обязательный)
- `flyerProgram: bool` - Включен ли продукт в программу "Флаер" (по умолчанию False)
- `dishOfDay: bool` - Включен ли продукт в "Блюдо дня" (по умолчанию False)

#### `Product`
Класс для описания элемента номенклатуры при импорте:
```python
from iiko_api.models import Product, ProductType, Color

product = Product(
    name="Новое блюдо",
    description="Описание блюда",
    type=ProductType.DISH,
    mainUnit="uuid-единицы-измерения",
    defaultSalePrice=500,
    color=Color(red=255, green=0, blue=0)
)
```

**Основные атрибуты:**
- `name: str` - Название элемента номенклатуры (обязательный)
- `type: ProductType` - Тип элемента номенклатуры (обязательный)
- `mainUnit: str` - ID основной единицы измерения (обязательный)
- `description: str | None` - Описание элемента
- `parent: str | None` - ID родительской группы номенклатуры
- `taxCategory: str | None` - ID налоговой категории
- `category: str | None` - ID категории
- `color: Color | None` - Цвет фона оформления кнопки в iikoFront
- `fontColor: Color | None` - Цвет шрифта кнопки в iikoFront
- `defaultSalePrice: int | None` - Цена продажи по умолчанию
- И другие опциональные поля

#### `AssemblyChart`
Класс для описания технологической карты при сохранении:
```python
from iiko_api.models import (
    AssemblyChart, 
    AssemblyChartItem, 
    ProductWriteoffStrategy,
    ProductSizeAssemblyStrategy,
    StoreSpecification
)

assembly_chart = AssemblyChart(
    assembledProductId="uuid-продукта",
    dateFrom="2024-01-01",
    dateTo="2024-12-31",
    assembledAmount=1.0,
    productWriteoffStrategy=ProductWriteoffStrategy.DIRECT,
    effectiveDirectWriteoffStoreSpecification=StoreSpecification(departments=[], inverse=False),
    productSizeAssemblyStrategy=ProductSizeAssemblyStrategy.COMMON,
    items=[AssemblyChartItem(...)],
    technologyDescription="Технология приготовления",
    description="Описание",
    appearance="Требования к оформлению",
    organoleptic="Органолептические показатели",
    outputComment="Суммарный выход"
)
```

**Основные атрибуты:**
- `assembledProductId: str` - UUID продукта, для которого создается техкарта (обязательный)
- `dateFrom: str` - Дата начала действия техкарты в формате "yyyy-MM-dd" (обязательный)
- `dateTo: str | None` - Дата окончания действия техкарты в формате "yyyy-MM-dd" (null - без ограничения)
- `assembledAmount: float` - Количество готового продукта
- `productWriteoffStrategy: ProductWriteoffStrategy` - Метод списания
- `effectiveDirectWriteoffStoreSpecification: StoreSpecification` - Спецификация подразделений для прямого списания
- `productSizeAssemblyStrategy: ProductSizeAssemblyStrategy` - Стратегия сборки по размерам
- `items: list[AssemblyChartItem]` - Список ингредиентов техкарты
- `technologyDescription: str` - Комментарий "Технология приготовления"
- `description: str` - Комментарий "Описание"
- `appearance: str` - Комментарий "Требования к оформлению и реализации"
- `organoleptic: str` - Комментарий "Органолептические показатели качества"
- `outputComment: str` - Суммарный выход

#### `AssemblyChartItem`
Класс для описания ингредиента технологической карты:
```python
from iiko_api.models import AssemblyChartItem, StoreSpecification

item = AssemblyChartItem(
    sortWeight=0,
    productId="uuid-ингредиента",
    amountIn=1.0,
    amountMiddle=0.5,
    amountOut=0.8,
    storeSpecification=StoreSpecification(departments=["uuid-отдела"], inverse=False)
)
```

**Основные атрибуты:**
- `productId: str` - UUID продукта-ингредиента (обязательный)
- `amountIn: float` - Количество на входе
- `amountMiddle: float` - Количество в процессе (обязательное поле, API не принимает null)
- `amountOut: float` - Выход готового продукта в единицах измерения
- `storeSpecification: StoreSpecification | None` - Спецификация склада/подразделения
- И другие опциональные поля

### Вспомогательные классы

#### `Color`
Класс для описания цвета:
```python
from iiko_api.models import Color

color = Color(red=255, green=128, blue=0)
```

**Атрибуты:**
- `red: int` - Значение красного канала (0-255)
- `green: int` - Значение зеленого канала (0-255)
- `blue: int` - Значение синего канала (0-255)

#### `StoreSpecification`
Структура для указания подмножества подразделений, в которых действует строка техкарты:
```python
from iiko_api.models import StoreSpecification

spec = StoreSpecification(
    departments=["uuid-отдела-1", "uuid-отдела-2"],
    inverse=False  # false - включающий фильтр, true - исключающий
)
```

**Атрибуты:**
- `departments: list[str]` - Список ID подразделений
- `inverse: bool` - false - фильтр включающий (строка действует для всех перечисленных подразделений), true - фильтр исключающий (строка действует для всех подразделений, КРОМЕ перечисленных)

### Перечисления (Enums)

#### `Status`
Статус приказа:
- `Status.NEW` - Новый приказ (сейчас может быть только NEW)

#### `ProductType`
Типы элементов номенклатуры:
- `ProductType.GOODS` - Товар
- `ProductType.DISH` - Блюдо
- `ProductType.PREPARED` - Заготовка (полуфабрикат)
- `ProductType.MODIFIER` - Модификатор
- `ProductType.SERVICE` - Услуга
- `ProductType.RATE` - Тариф (дочерний элемент для услуги)

#### `ReferenceType`
Типы справочников для работы с API iiko:
- `ReferenceType.MEASURE_UNIT` - Единицы измерения
- `ReferenceType.TAX_CATEGORY` - Налоговые категории
- `ReferenceType.ACCOUNTING_CATEGORY` - Бухгалтерские категории
- `ReferenceType.PRODUCT_CATEGORY` - Пользовательские категории продуктов

#### `ProductWriteoffStrategy`
Метод списания технологической карты:
- `ProductWriteoffStrategy.ASSEMBLE` - Списывать готовое блюдо
- `ProductWriteoffStrategy.DIRECT` - Списывать ингредиенты

#### `ProductSizeAssemblyStrategy`
Стратегия сборки по размерам блюда:
- `ProductSizeAssemblyStrategy.COMMON` - Общая техкарта для всех размеров
- `ProductSizeAssemblyStrategy.INDIVIDUAL` - Индивидуальная техкарта для каждого размера

## Сервисы

### IikoPriceOrderService

Сервис для упрощенной работы с приказами на установку цен.

```python
from iiko_api import IikoApi, IikoPriceOrderService
from iiko_api.models import Item

iiko_client = IikoApi(...)
price_service = IikoPriceOrderService(iiko_client)

# Формирование приказа для установки цен
dishes = [
    Item(departmentId="uuid", productId="uuid", price=500),
    Item(departmentId="uuid", productId="uuid", price=750)
]
price_service.set_price(dishes=dishes, order_date="2024-12-23")
```

#### Методы

- `set_price(dishes: list[Item], order_date: str) -> None`
    Формирует приказ для заведения со списком блюд и датой приказа.
    - `dishes` - Список блюд (в поле `price` должна быть указана новая цена)
    - `order_date` - Дата приказа в формате "yyyy-MM-dd"

## Обработка исключений

Библиотека использует специфичные исключения для различных типов ошибок. Все исключения наследуются от стандартных исключений Python или `requests.exceptions`.

### Исключения библиотеки

#### `IikoAPIError`
Исключение для бизнес-ошибок API iiko (когда HTTP 200, но `result != SUCCESS`).

```python
from iiko_api import IikoApi, IikoAPIError

try:
    product = iiko_client.nomenclature.import_product(product_data)
except IikoAPIError as e:
    print(f"Ошибка API: {e}")
    print(f"Детали ошибок: {e.errors}")
```

#### `IikoNotFoundError` (базовый класс)
Базовое исключение для случаев, когда сущность не найдена (HTTP 404).

#### `RoleNotFoundError`
Исключение, возникающее когда роль не найдена по ID.

```python
from iiko_api import IikoApi, RoleNotFoundError

try:
    role = iiko_client.roles.get_role_by_id("role-id")
except RoleNotFoundError as e:
    print(f"Роль не найдена: {e}")
    print(f"ID роли: {e.role_id}")
```

#### `EmployeeNotFoundError`
Исключение, возникающее когда сотрудник не найден по ID.

```python
from iiko_api import IikoApi, EmployeeNotFoundError

try:
    employee = iiko_client.employees.get_employee_by_id(employee_id)
except EmployeeNotFoundError as e:
    print(f"Сотрудник не найден: {e}")
    print(f"ID сотрудника: {e.employee_id}")
```

#### `IikoTimeoutError`
Исключение, возникающее при превышении таймаута запроса к API iiko.

```python
from iiko_api import IikoApi, IikoTimeoutError

try:
    employees = iiko_client.employees.get_employees()
except IikoTimeoutError as e:
    print(f"Превышено время ожидания: {e}")
    # Можно попробовать увеличить timeout при инициализации:
    # iiko_client = IikoApi(base_url, login, password, timeout=60.0)
```

#### `IikoConnectionError`
Исключение, возникающее при ошибке подключения к API iiko.

```python
from iiko_api import IikoApi, IikoConnectionError

try:
    employees = iiko_client.employees.get_employees()
except IikoConnectionError as e:
    print(f"Ошибка подключения: {e}")
```

### Пример обработки всех исключений

```python
from iiko_api import (
    IikoApi,
    IikoAPIError,
    IikoNotFoundError,
    RoleNotFoundError,
    EmployeeNotFoundError,
    IikoTimeoutError,
    IikoConnectionError
)
from requests.exceptions import HTTPError
import json

try:
    # Ваш код работы с API
    employees = iiko_client.employees.get_employees()
    role = iiko_client.roles.get_role_by_id("role-id")
    product = iiko_client.nomenclature.import_product(product_data)
    
except IikoAPIError as e:
    # Бизнес-ошибка API (HTTP 200, но result=ERROR)
    print(f"Ошибка API: {e}")
    for error in e.errors:
        print(f"  Код: {error.get('code')}, Сообщение: {error.get('value')}")
        
except (RoleNotFoundError, EmployeeNotFoundError) as e:
    # Сущность не найдена
    print(f"Не найдено: {e}")
    print(f"ID: {e.entity_id}")
    
except IikoTimeoutError as e:
    # Превышен таймаут
    print(f"Таймаут: {e}")
    # Можно увеличить timeout или повторить запрос
    
except IikoConnectionError as e:
    # Ошибка подключения
    print(f"Ошибка подключения: {e}")
    # Проверьте доступность сервера
    
except HTTPError as e:
    # Другие HTTP ошибки (4xx, 5xx)
    print(f"HTTP ошибка {e.response.status_code}: {e}")
    
except ValueError as e:
    # Ошибки валидации (неверный формат данных, пустые параметры и т.д.)
    print(f"Ошибка валидации: {e}")
    
except json.JSONDecodeError as e:
    # Ошибка парсинга JSON
    print(f"Ошибка парсинга JSON: {e}")
    
except Exception as e:
    # Неожиданные ошибки
    print(f"Неожиданная ошибка: {e}")
```

## Параметры инициализации

При создании экземпляра `IikoApi` можно указать таймаут для HTTP запросов:

```python
iiko_client = IikoApi(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS"),
    timeout=60.0  # Таймаут в секундах (по умолчанию 30)
)
```

