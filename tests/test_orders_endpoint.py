"""
Тесты для OrdersEndpoints
"""
import json
from unittest.mock import Mock

import pytest

from iiko_api.endpoints.orders import OrdersEndpoints
from iiko_api.exceptions import IikoAPIError
from iiko_api.models.models import Order


def test_set_new_order_success(mock_base_client, mock_success_response):
    """Тест успешного создания приказа"""
    mock_base_client.post.return_value = mock_success_response

    endpoint = OrdersEndpoints(mock_base_client)
    order = Order(
        dateIncoming="2024-01-01",
        shortName="Test Order",
        items=[]
    )

    result = endpoint.set_new_order(order)

    assert result == {"id": "123", "name": "Test"}
    mock_base_client.post.assert_called_once()


def test_set_new_order_api_error(mock_base_client, mock_error_response):
    """Тест обработки ошибки API при создании приказа"""
    mock_base_client.post.return_value = mock_error_response

    endpoint = OrdersEndpoints(mock_base_client)
    order = Order(
        dateIncoming="2024-01-01",
        shortName="Test Order",
        items=[]
    )

    with pytest.raises(IikoAPIError) as exc_info:
        endpoint.set_new_order(order)

    assert "Ошибка при создании приказа" in str(exc_info.value)
    assert len(exc_info.value.errors) > 0


def test_set_new_order_invalid_json(mock_base_client):
    """Тест обработки невалидного JSON"""
    response = Mock()
    response.status_code = 200
    response.text = "Invalid JSON"
    response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_base_client.post.return_value = response

    endpoint = OrdersEndpoints(mock_base_client)
    order = Order(
        dateIncoming="2024-01-01",
        shortName="Test Order",
        items=[]
    )

    with pytest.raises(ValueError) as exc_info:
        endpoint.set_new_order(order)

    assert "невалидный JSON" in str(exc_info.value)


def test_get_price_list_success(mock_base_client, mock_response):
    """Тест успешного получения цен"""
    mock_response.json.return_value = {"prices": []}
    mock_base_client.get.return_value = mock_response

    endpoint = OrdersEndpoints(mock_base_client)

    result = endpoint.get_price_list(date_from="2024-01-01")

    assert result == {"prices": []}
    mock_base_client.get.assert_called_once()


def test_get_price_list_empty_date_from(mock_base_client):
    """Тест валидации пустого date_from"""
    endpoint = OrdersEndpoints(mock_base_client)

    with pytest.raises(ValueError) as exc_info:
        endpoint.get_price_list(date_from="")

    assert "date_from" in str(exc_info.value).lower()
