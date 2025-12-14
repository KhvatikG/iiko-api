"""
Тесты для NomenclatureEndpoints
"""
from unittest.mock import Mock

import pytest

from iiko_api.endpoints.nomenclature import NomenclatureEndpoints
from iiko_api.exceptions import IikoAPIError
from iiko_api.models.models import Product, ProductType


def test_import_product_success(mock_base_client, mock_success_response):
    """Тест успешного импорта продукта"""
    mock_base_client.post.return_value = mock_success_response
    
    endpoint = NomenclatureEndpoints(mock_base_client)
    product = Product(
        name="Test Product",
        mainUnit="unit-id",
        type=ProductType.DISH
    )
    
    result = endpoint.import_product(product)
    
    assert result == {"id": "123", "name": "Test"}
    mock_base_client.post.assert_called_once()


def test_import_product_api_error(mock_base_client, mock_error_response):
    """Тест обработки ошибки API при импорте продукта"""
    mock_base_client.post.return_value = mock_error_response
    
    endpoint = NomenclatureEndpoints(mock_base_client)
    product = Product(
        name="Test Product",
        mainUnit="unit-id",
        type=ProductType.DISH
    )
    
    with pytest.raises(IikoAPIError) as exc_info:
        endpoint.import_product(product)
    
    assert "Ошибка при импорте продукта" in str(exc_info.value)


def test_import_product_no_response_field(mock_base_client):
    """Тест обработки ответа без поля response"""
    response = Mock()
    response.status_code = 200
    response.text = '{"result": "SUCCESS"}'
    response.json.return_value = {"result": "SUCCESS"}
    response.request = Mock()
    response.request.url = "https://test.iiko.com/api"
    response.request.method = "POST"
    response.request.body = None
    mock_base_client.post.return_value = response
    
    endpoint = NomenclatureEndpoints(mock_base_client)
    product = Product(
        name="Test Product",
        mainUnit="unit-id",
        type=ProductType.DISH
    )
    
    # Должен вернуть весь ответ, если response отсутствует
    result = endpoint.import_product(product)
    assert result == {"result": "SUCCESS"}
