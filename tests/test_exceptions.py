"""
Тесты для исключений iiko-api
"""
import pytest

from iiko_api.exceptions import (
    EmployeeNotFoundError,
    IikoAPIError,
    IikoConnectionError,
    IikoNotFoundError,
    IikoTimeoutError,
    RoleNotFoundError,
)


def test_iiko_api_error():
    """Тест IikoAPIError"""
    errors = [{"code": "E001", "value": "Test error"}]
    error = IikoAPIError("Test message", errors=errors)
    
    assert str(error) == "Test message"
    assert error.errors == errors


def test_iiko_not_found_error():
    """Тест IikoNotFoundError"""
    error = IikoNotFoundError("Entity not found", entity_id="123")
    
    assert str(error) == "Entity not found"
    assert error.entity_id == "123"


def test_role_not_found_error():
    """Тест RoleNotFoundError"""
    error = RoleNotFoundError("role-123", server_message="Role does not exist")
    
    assert "role-123" in str(error)
    assert "Role does not exist" in str(error)
    assert error.role_id == "role-123"
    assert error.entity_id == "role-123"


def test_employee_not_found_error():
    """Тест EmployeeNotFoundError"""
    error = EmployeeNotFoundError("emp-123", server_message="Employee not found")
    
    assert "emp-123" in str(error)
    assert "Employee not found" in str(error)
    assert error.employee_id == "emp-123"
    assert error.entity_id == "emp-123"


def test_iiko_timeout_error():
    """Тест IikoTimeoutError"""
    original = Exception("Original timeout")
    error = IikoTimeoutError("Timeout occurred", original_exception=original)
    
    assert "Timeout occurred" in str(error)
    assert isinstance(error, IikoTimeoutError)
    assert error.original_exception == original
    # Проверяем, что не наследуется от RequestException
    from requests.exceptions import RequestException
    assert not isinstance(error, RequestException)


def test_iiko_connection_error():
    """Тест IikoConnectionError"""
    original = Exception("Original connection error")
    error = IikoConnectionError("Connection failed", original_exception=original)
    
    assert "Connection failed" in str(error)
    assert isinstance(error, IikoConnectionError)
    assert error.original_exception == original
    # Проверяем, что не наследуется от RequestException
    from requests.exceptions import RequestException
    assert not isinstance(error, RequestException)
