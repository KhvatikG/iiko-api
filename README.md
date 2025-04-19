## README.md

# iiko-api

Библиотека для работы с API iiko.

## Описание

Библиотека предоставляет базовый класс `IikoApi` для работы с API iiko. 
Этот класс предоставляет методы для выполнения GET и POST запросов к API, 
а также методы для аутентификации и отмены аутентификации.

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

iiko_api = IikoApi(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS")
)

# Получение списка всех сотрудников
employees = iiko_api.employees.get_employees()

# Получение списка всех ролей
roles = iiko_api.roles.get_roles()
```
## Аутентификация
#### *IikoApi представляет контекстный менеджер для авторизованного выполнения блока кода и декоратор:*
```python
from iiko_api import IikoApi
from dotenv import dotenv_values

# Если используем .env подгружаем из него данные для конфигурации
config = dotenv_values(".env")

iiko_api = IikoApi(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS")
)

# Аутентификация через декоратор
@iiko_api.with_authorization
def my_function():
    """Несколько обращений к iiko с использованием IikoApi get | post"""
    iiko_api.client.get('/resto/api/employees/')
    iiko_api.client.post(...)

# Аутентификация через контекчтный менеджер
with iiko_api.auth_context():
  iiko_api.client.get('/resto/api/employees/')
  iiko_api.client.post(...)
```
В представленном примере все обращения в рамках функции или контекстного менеджера будут выполнены в рамках одной авторизованной сессии.
Методы `client.get` и `client.post` уже содержат `BASE_URL` и ожидают только конечную точку.
post так-же может принимать заголоки и тело:   
`post(endpoint: str, data: dict[str, Any] = None, headers: dict[str, Any] = None)`
 


## Эндпоинты и методы
#### *Сейчас почти все представленные в этом разделе запросы автоматически аутентифицируются и отпускают токен по завершению, в дальнейшем это будет конфигурируемым параметром*
### IikoApi.employees - Ендпоинты для работы с сотрудниками.
- ```get_employees() -> list[dict]``` - Возвращает всех сотрудников в виде списка словарей.
- ```get_employee_by_id(employee_id: uuid) -> dict``` - Возвращает сотрудника по id
- ```get_employees_by_department(department_code: str) -> list[dict]``` - Возвращает сотрудников определенного отдела по его коду.
- ```get_attendances_for_department(department_code: str,date_from: datetime,date_to: datetime) -> list[dict]``` - Возвращает список явок сотрудников для отдела за период
  
### IikoApi.roles - Ендроинты для работы с ролями
- ```get_roles() -> list[dict]``` - Возвращает список всех ролей.
- ```get_role_by_id(role_id: str) -> dict``` - Возвращает роль по её id

### IikoApi.reports - Отчеты
- get_sales_report:
    ```
    get_sales_report(
    date_from: datetime, date_to: datetime, department_id: str, date_aggregation: bool = True
    ) -> dict[date, float] | list[dict]
    ```
    Получение отчета по продажам за период.
    Возвращает словарь, где ключ это дата, а значение это выручка, если date_aggregation=True
    Если date_aggregation=False, то отчет будет списком словарей с ключами date и value.

### IikoApi.nomenclature - Номенклатура

- get_nomenclature_list:
    ```
    get_nomenclature_list(
                          articles: list[str] | None = None,
                          ids: list[str] | None = None,
                          types: list[str] | None = None,
                          include_deleted: bool = False,
                          ) -> list[dict] | None
    ```
    Получение списка элементов номенклатуры с фильтрацией по артикулу, по id и по типу элемента номенклатуры.
    Возвращает список словарей, где каждый словарь представляет элемент номенклатуры

- get_nomenclature_groups:
    ```
    get_nomenclature_groups(
            ids: list[str] | None = None,
            parent_ids: list[str] | None = None,
            nums: list[str] | None = None,
            include_deleted: bool = False,
    ) -> list[dict] | None
    ```
    Получение списка групп номенклатуры с фильтрами по id, id родительской категории, артикулу.
    Список словарей, где каждый словарь представляет группу номенклатуры.

### IikoApi.orders - Приказы
- set_new_order(order: Order) - Создание нового приказа в iiko
    Приказ необходимо создать используя классы из iiko_api.models
    Класс приказа:
    ```python
    from pydantic import BaseModel
  
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
    ```
    Каждое блюдо, включённое в приказ, представляется экземпляром класса Item:
    ```python
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
    ```
- get_price_list:
    ```
    get_price_list(
            date_from: str,  - в формате "yyyy-MM-dd"
            date_to: str = None,  - в формате "yyyy-MM-dd"
            type_: str = "BASE",  - Тип цены для выгрузки BASE(Цена на всем интервале) | SCHEDULED(цена по расписанию)
            department_id: str | list = None
    ) -> dict | None
    ```
  Получение цен установленных приказами

### IikoApi.assembly_charts - Тех карты
- get_all_assembly_charts:
    ```
  get_all_assembly_charts(
            date_from: str,  - в формате "yyyy-MM-dd"
            date_to: str = None,  - в формате "yyyy-MM-dd"
            include_prepared_charts: bool = True,
            include_deleted_products: bool = False
    ) -> dict | None:
  ```
  Получение всех техкарт.
  Возвращает словарь с ключами:  
  <br/>
  ```assemblyCharts``` - Список исходных технологических карт,
  интервал действия которых пересекает запрошенный интервал.  
  <br/>
  ```preparedCharts``` - Список разложенных до ингредиентов технологических карт,
  интервал действия которых пересекает запрошенный интервал.

### IikoApi.stores - Склады
- get_stores(auto_login=True) -> list | None - Получение списка складов
- get_stores_balance(timestamp: str = "now", auto_login=True) -> list | None:
    Получение остатков на складах  
    `timestamp` - Время, на которое необходимо получить остатки в формате "yyyy-MM-dd", если "now" то вернет на текущее время

### IikoApi.olap - OLAP отчеты
- get_olap_by_preset_id:
  ```
  get_olap_by_preset_id(
            preset_id: str, - UUID пресета в iiko(можно получить по /resto/api/v2/reports/olap/presets)
            date_from: datetime = None,
            date_to: datetime = None, - Не включается в отчет и должна быть больше чем date_from
            auto_login: bool = True - Автологин, при групповых запросвх в контекстном менеджере iiko_api.auth_context 
                                      или через декоратор with_authorization - установить False.
    ) -> dict:
  ```

## Примечания

- В дальнейшем будет возможность настроить логирование и передавать другие параметры при инициализации клиента.
---
TODO:
- Сделать авто-аутентификацию отключаемым параметром для всех методов связанных с конечными точками.


