from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from requests import Response

from iiko_api.core import BaseClient

OLAP_ENDPOINT = "/resto/api/v2/reports/olap"
MONEY_QUANT = Decimal("0.01")


def _as_date(value: datetime | date) -> date:
    return value.date() if isinstance(value, datetime) else value


def _olap_day_start(value: datetime | date) -> str:
    return _as_date(value).strftime("%Y-%m-%dT00:00:00.000")


def _parse_olap_day(raw_date: Any) -> date:
    text = str(raw_date).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError as e:
        raise ValueError(f"Некорректная дата в OLAP ответе: {raw_date!r}") from e


def _parse_decimal(value: Any, *, field: str) -> Decimal:
    """Parse OLAP numeric values without float binary artifacts."""
    if value is None or value == "":
        return Decimal("0")
    if isinstance(value, bool):
        raise ValueError(f"Некорректное значение {field} в OLAP ответе: {value!r}")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Некорректное значение {field} в OLAP ответе: {value!r}")
        # JSON may still arrive as float if parse_float was not used; avoid Decimal(float).
        return Decimal(format(value, ".10f"))
    if isinstance(value, str):
        text = value.strip().replace(" ", "").replace(",", ".")
        if not text:
            return Decimal("0")
        try:
            return Decimal(text)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Некорректное значение {field} в OLAP ответе: {value!r}") from e
    raise ValueError(f"Некорректное значение {field} в OLAP ответе: {value!r}")


def _parse_money_decimal(value: Any, *, field: str) -> Decimal:
    """Money amount as Decimal with 0.01 scale (HALF_UP)."""
    return _parse_decimal(value, field=field).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _response_json_object(result: Response) -> dict[str, Any]:
    try:
        # Prefer Decimal for JSON numbers so sales never become binary floats.
        payload = result.json(parse_float=Decimal)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(
            f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
        ) from e
    if not isinstance(payload, dict):
        raise ValueError("API вернул неожиданный JSON (ожидался object)")
    return payload


def build_fiscal_sales_olap_body(
    date_from: datetime | date,
    date_to: datetime | date,
    department_id: str,
) -> dict[str, Any]:
    if not str(department_id).strip():
        raise ValueError("department_id не может быть пустым")
    start = _as_date(date_from)
    end = _as_date(date_to)
    if start > end:
        raise ValueError("date_from должен быть меньше или равен date_to")
    return {
        "reportType": "SALES",
        "buildSummary": False,
        "groupByRowFields": ["OpenDate.Typed"],
        "groupByColFields": [],
        "aggregateFields": ["DishDiscountSumInt"],
        "filters": {
            "OpenDate.Typed": {
                "filterType": "DateRange",
                "periodType": "CUSTOM",
                "from": _olap_day_start(start),
                "to": _olap_day_start(end + timedelta(days=1)),
                "includeLow": True,
                "includeHigh": False,
            },
            "Department.Id": {
                "filterType": "IncludeValues",
                "values": [department_id],
            },
            "PayTypes.IsPrintCheque": {
                "filterType": "IncludeValues",
                "values": ["FISCAL"],
            },
        },
    }


class OLAP:
    """Класс представляющий методы работы с OLAP отчетами."""

    def __init__(self, client: BaseClient):
        self.client = client

    def get_olap_by_preset_id(
        self,
        preset_id: str,
        date_from: datetime | date | None = None,
        date_to: datetime | date | None = None,
        auto_login: bool = True,
    ) -> dict:
        """
        Получить отчет по ID преднастроенного отчета.

        :param preset_id: UUID преднастроенного отчета
        :param date_from: дата начала отчета (включается в отчет); date или datetime
        :param date_to: дата конца отчета (не включается в отчет); date или datetime
        :param auto_login: оставлен для обратной совместимости, не используется
        """
        del auto_login
        try:
            UUID(preset_id)
        except ValueError:
            raise ValueError("preset_id должен быть валидным UUID") from None

        if date_from is not None and not isinstance(date_from, date):
            raise TypeError("date_from должен быть типа date или datetime")
        if date_to is not None and not isinstance(date_to, date):
            raise TypeError("date_to должен быть типа date или datetime")

        start = _as_date(date_from) if date_from is not None else None
        end = _as_date(date_to) if date_to is not None else None
        if start is not None and end is not None and start == end:
            raise ValueError("date_from и date_to должны быть разными")
        if start is not None and end is not None and start > end:
            raise ValueError("date_from должен быть меньше date_to")

        url = "/resto/api/v2/reports/olap/byPresetId/" + str(preset_id)

        today = date.today()
        date_from_str = (start or today).isoformat()
        date_to_str = (end or (today + timedelta(days=1))).isoformat()

        params = {"dateFrom": date_from_str, "dateTo": date_to_str}
        result: Response = self.client.get(url, params=params)
        return _response_json_object(result)

    def query_olap(self, body: dict[str, Any]) -> dict[str, Any]:
        """Произвольный OLAP-запрос (POST /resto/api/v2/reports/olap)."""
        if not isinstance(body, dict) or not body:
            raise ValueError("body должен быть непустым dict")
        result = self.client.post(OLAP_ENDPOINT, json=body)
        return _response_json_object(result)

    def get_fiscal_sales_olap_raw(
        self,
        date_from: datetime | date,
        date_to: datetime | date,
        department_id: str,
    ) -> dict[str, Any]:
        """Сырой fiscal OLAP SALES payload (DishDiscountSumInt, FISCAL)."""
        if not str(department_id).strip():
            raise ValueError("department_id не может быть пустым")
        return self.query_olap(build_fiscal_sales_olap_body(date_from, date_to, department_id))

    def get_fiscal_sales_by_day(
        self,
        date_from: datetime | date,
        date_to: datetime | date,
        department_id: str,
    ) -> dict[date, Decimal]:
        """
        Фискальная выручка по дням как Decimal (не float).

        Поле: DishDiscountSumInt, фильтр PayTypes.IsPrintCheque=FISCAL.
        Суммы квантуются до 0.01 (HALF_UP).
        """
        payload = self.get_fiscal_sales_olap_raw(date_from, date_to, department_id)
        sales: dict[date, Decimal] = {}
        for row in payload.get("data") or []:
            if not isinstance(row, dict):
                continue
            raw_date = row.get("OpenDate.Typed")
            if not raw_date:
                continue
            day = _parse_olap_day(raw_date)
            sales[day] = _parse_money_decimal(
                row.get("DishDiscountSumInt"),
                field="DishDiscountSumInt",
            )
        return sales
