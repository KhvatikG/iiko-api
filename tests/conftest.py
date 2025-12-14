"""
Конфигурация pytest для тестов iiko-api
"""
from unittest.mock import Mock

import pytest
from requests import Response

from iiko_api.core.base_client import BaseClient


@pytest.fixture
def mock_base_client():
    """Создает мок BaseClient для тестирования"""
    client = Mock(spec=BaseClient)
    client.base_url = "https://test.iiko.com"
    client.session = Mock()
    return client


@pytest.fixture
def mock_response():
    """Создает мок Response объекта"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.ok = True
    response.text = ""
    response.json.return_value = {}
    response.request = Mock()
    response.request.url = "https://test.iiko.com/api"
    response.request.method = "GET"
    response.request.body = None
    return response


@pytest.fixture
def mock_success_response():
    """Создает мок успешного JSON ответа с result=SUCCESS"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.ok = True
    response.text = '{"result": "SUCCESS", "response": {"id": "123"}}'
    response.json.return_value = {
        "result": "SUCCESS",
        "response": {"id": "123", "name": "Test"}
    }
    response.request = Mock()
    response.request.url = "https://test.iiko.com/api"
    response.request.method = "POST"
    response.request.body = None
    return response


@pytest.fixture
def mock_error_response():
    """Создает мок ответа с ошибкой API (result=ERROR)"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.ok = True
    response.text = '{"result": "ERROR", "errors": [{"code": "E001", "value": "Test error"}]}'
    response.json.return_value = {
        "result": "ERROR",
        "errors": [{"code": "E001", "value": "Test error"}]
    }
    response.request = Mock()
    response.request.url = "https://test.iiko.com/api"
    response.request.method = "POST"
    response.request.body = None
    return response
