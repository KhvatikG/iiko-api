"""Fiscal OLAP helpers, Decimal parsing, and preset date support."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from iiko_api.endpoints.olap import (
    OLAP,
    _parse_decimal,
    _parse_money_decimal,
    build_fiscal_sales_olap_body,
)


def test_build_fiscal_sales_olap_body_is_inclusive_of_end_day() -> None:
    body = build_fiscal_sales_olap_body(date(2026, 7, 1), date(2026, 7, 31), "dept-1")
    assert body["aggregateFields"] == ["DishDiscountSumInt"]
    assert body["filters"]["PayTypes.IsPrintCheque"]["values"] == ["FISCAL"]
    assert body["filters"]["OpenDate.Typed"]["from"] == "2026-07-01T00:00:00.000"
    assert body["filters"]["OpenDate.Typed"]["to"] == "2026-08-01T00:00:00.000"
    assert body["filters"]["Department.Id"]["values"] == ["dept-1"]


def test_build_fiscal_sales_olap_body_rejects_blank_department() -> None:
    with pytest.raises(ValueError, match="department_id"):
        build_fiscal_sales_olap_body(date(2026, 7, 1), date(2026, 7, 1), "  ")


def test_query_olap_posts_body() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"data": []}
    client.post.return_value = response
    olap = OLAP(client)
    body = {"reportType": "SALES", "aggregateFields": ["DishDiscountSumInt"]}
    assert olap.query_olap(body) == {"data": []}
    client.post.assert_called_once()
    args, kwargs = client.post.call_args
    assert args[0] == "/resto/api/v2/reports/olap"
    assert kwargs["json"] is body


def test_query_olap_rejects_empty_body() -> None:
    with pytest.raises(ValueError, match="непустым"):
        OLAP(MagicMock()).query_olap({})


def test_get_fiscal_sales_by_day_uses_decimal() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        "data": [{"OpenDate.Typed": "2026-07-10T00:00:00.000", "DishDiscountSumInt": "1234.56"}]
    }
    client.post.return_value = response
    olap = OLAP(client)
    sales = olap.get_fiscal_sales_by_day(date(2026, 7, 10), date(2026, 7, 10), "dept-1")
    assert sales == {date(2026, 7, 10): Decimal("1234.56")}
    client.post.assert_called_once()
    _, kwargs = client.post.call_args
    assert kwargs["json"]["filters"]["PayTypes.IsPrintCheque"]["values"] == ["FISCAL"]


def test_get_fiscal_sales_by_day_rejects_bad_amount() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        "data": [{"OpenDate.Typed": "2026-07-10", "DishDiscountSumInt": "not-a-number"}]
    }
    client.post.return_value = response
    with pytest.raises(ValueError, match="DishDiscountSumInt"):
        OLAP(client).get_fiscal_sales_by_day(date(2026, 7, 10), date(2026, 7, 10), "dept-1")


def test_get_fiscal_sales_by_day_rejects_bad_date() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        "data": [{"OpenDate.Typed": "not-a-date", "DishDiscountSumInt": 1}]
    }
    client.post.return_value = response
    with pytest.raises(ValueError, match="Некорректная дата"):
        OLAP(client).get_fiscal_sales_by_day(date(2026, 7, 10), date(2026, 7, 10), "dept-1")


def test_parse_decimal_from_json_float_avoids_binary_noise() -> None:
    # Typical JSON number path if parse_float was not applied.
    amount = _parse_money_decimal(10.1 + 0.2, field="DishDiscountSumInt")
    assert amount == Decimal("10.30")


def test_parse_decimal_from_string_and_int() -> None:
    assert _parse_decimal("1 234,56", field="x") == Decimal("1234.56")
    assert _parse_decimal(100, field="x") == Decimal(100)
    assert _parse_decimal(Decimal("1.5"), field="x") == Decimal("1.5")


def test_parse_decimal_rejects_bool_and_nan() -> None:
    with pytest.raises(ValueError):
        _parse_decimal(True, field="x")
    with pytest.raises(ValueError):
        _parse_decimal(float("nan"), field="x")


def test_response_json_uses_parse_float_decimal() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        "data": [{"OpenDate.Typed": "2026-07-10", "DishDiscountSumInt": Decimal("99.99")}]
    }
    client.post.return_value = response
    sales = OLAP(client).get_fiscal_sales_by_day(date(2026, 7, 10), date(2026, 7, 10), "dept-1")
    assert sales[date(2026, 7, 10)] == Decimal("99.99")
    response.json.assert_called_with(parse_float=Decimal)


def test_get_olap_by_preset_id_accepts_date() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"data": []}
    client.get.return_value = response
    preset = "11111111-1111-1111-1111-111111111111"
    OLAP(client).get_olap_by_preset_id(
        preset,
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 2),
    )
    args, kwargs = client.get.call_args
    assert preset in args[0]
    assert kwargs["params"] == {"dateFrom": "2026-07-01", "dateTo": "2026-07-02"}


def test_get_olap_by_preset_id_accepts_datetime_and_normalizes_same_day() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"data": []}
    client.get.return_value = response
    preset = "11111111-1111-1111-1111-111111111111"
    with pytest.raises(ValueError, match="разными"):
        OLAP(client).get_olap_by_preset_id(
            preset,
            date_from=datetime(2026, 7, 1, 10, 0),
            date_to=datetime(2026, 7, 1, 18, 0),
        )
