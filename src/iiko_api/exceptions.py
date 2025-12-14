"""
Модуль с кастомными исключениями для iiko API
"""

class IikoAPIError(Exception):
    """Исключение для бизнес-ошибок API iiko (когда HTTP 200, но result != SUCCESS)"""
    def __init__(self, message: str, errors: list[dict] = None):
        self.errors = errors or []
        super().__init__(message)


class IikoNotFoundError(Exception):
    """Базовое исключение для случаев, когда сущность не найдена (HTTP 404)"""
    def __init__(self, message: str, entity_id: str = None):
        self.entity_id = entity_id
        super().__init__(message)


class RoleNotFoundError(IikoNotFoundError):
    """Исключение, возникающее когда роль не найдена по ID"""
    def __init__(self, role_id: str, server_message: str = None):
        self.role_id = role_id
        message = f"Роль с ID {role_id} не найдена"
        if server_message:
            message += f". Сообщение сервера: {server_message}"
        super().__init__(message, entity_id=role_id)


class EmployeeNotFoundError(IikoNotFoundError):
    """Исключение, возникающее когда сотрудник не найден по ID"""
    def __init__(self, employee_id: str, server_message: str = None):
        self.employee_id = employee_id
        message = f"Сотрудник с ID {employee_id} не найден"
        if server_message:
            message += f". Сообщение сервера: {server_message}"
        super().__init__(message, entity_id=employee_id)


class IikoTimeoutError(Exception):
    """
    Исключение, возникающее при превышении таймаута запроса к API iiko.
    
    Исходное исключение сохраняется
    в атрибуте original_exception.
    """
    def __init__(self, message: str = "Превышено время ожидания ответа от API iiko", original_exception: Exception = None):
        self.original_exception = original_exception
        super().__init__(message)


class IikoConnectionError(Exception):
    """
    Исключение, возникающее при ошибке подключения к API iiko.
    
    Исходное исключение сохраняется
    в атрибуте original_exception.
    """
    def __init__(self, message: str = "Ошибка подключения к API iiko", original_exception: Exception = None):
        self.original_exception = original_exception
        super().__init__(message)
