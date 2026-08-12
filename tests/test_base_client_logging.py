"""Tests for URL sanitization and body-redacted request logging."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from requests import Response
from requests.exceptions import HTTPError

from iiko_api.core.base_client import BaseClient, sanitize_url


def test_sanitize_url_strips_login_and_pass() -> None:
    url = "https://iiko.example/resto/api/auth?login=admin&pass=secret&x=1"
    cleaned = sanitize_url(url)
    assert "pass=" not in cleaned
    assert "login=" not in cleaned
    assert "x=1" in cleaned


def test_sanitize_url_failure_does_not_return_raw() -> None:
    class Boom:
        def __str__(self) -> str:
            raise RuntimeError("boom")

    assert sanitize_url(Boom()) == "<unparseable-url>"  # type: ignore[arg-type]


def test_success_logging_omits_bodies_by_default(caplog: pytest.LogCaptureFixture) -> None:
    client = BaseClient("https://iiko.example", "u", "h")
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "SECRET_BODY"
    response.request = MagicMock(url="https://iiko.example/x?pass=1", method="GET", body="SECRET_REQ")
    response.raise_for_status = MagicMock()

    with caplog.at_level("DEBUG"):
        client._log_exchange(response)

    joined = "\n".join(record.message for record in caplog.records)
    assert "SECRET_BODY" not in joined
    assert "SECRET_REQ" not in joined
    assert "pass=" not in joined


def test_log_bodies_true_includes_bodies(caplog: pytest.LogCaptureFixture) -> None:
    client = BaseClient("https://iiko.example", "u", "h", log_bodies=True)
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "SECRET_BODY"
    response.request = MagicMock(url="https://iiko.example/x", method="POST", body="SECRET_REQ")

    with caplog.at_level("DEBUG"):
        client._log_exchange(response)

    joined = "\n".join(record.message for record in caplog.records)
    assert "SECRET_BODY" in joined
    assert "SECRET_REQ" in joined


def test_http_error_does_not_log_bodies_by_default(caplog: pytest.LogCaptureFixture) -> None:
    client = BaseClient("https://iiko.example", "u", "h")
    response = MagicMock(spec=Response)
    response.status_code = 500
    response.text = "SECRET_BODY"
    response.request = MagicMock(
        url="https://iiko.example/x?login=admin",
        method="POST",
        body="SECRET_REQ",
        headers={"Authorization": "Bearer x"},
    )
    error = HTTPError("boom", response=response)
    response.raise_for_status = MagicMock(side_effect=error)

    original_get = client.session.get
    client.session.get = MagicMock(return_value=response)  # type: ignore[method-assign]
    try:
        with caplog.at_level("DEBUG"), pytest.raises(HTTPError):
            client.get("/x")
    finally:
        client.session.get = original_get  # type: ignore[method-assign]

    joined = "\n".join(record.message for record in caplog.records)
    assert "SECRET_BODY" not in joined
    assert "SECRET_REQ" not in joined
    assert "Bearer" not in joined
