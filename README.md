## README.md

# iiko-api

Библиотека для работы с API iiko.

## Описание

Библиотека предоставляет базовый класс `IikoApi` для работы с API iiko. 
Этот класс предоставляет методы для выполнения GET и POST запросов к API, 
а также методы для авторизации и отмены авторизации.

Библиотека также предоставляет классы `EmployeesEndpoints` и `RolesEndpoints`, 
которые предоставляют методы для работы с сотрудниками и ролями сотрудников соответственно.

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

## Примечания

- Для работы с API iiko требуется авторизация.
- В библиотеке используется логирование, которое можно настроить в файле logging_config.py.
- Для инициализации client файле .env должны быть установлены переменные BASE_URL, IIKO_LOGIN и IIKO_PASS.
- В дальнейшем будет возможность настроить логирование и передавать другие параметры при инициализации клиента.
---
TODO:
- Заменить принты на логирование


