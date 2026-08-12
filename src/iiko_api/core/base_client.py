"""
Модуль для работы с API iiko
Содержит Базовый класс для работы с API iiko.
Включающий методы: get, post
Методы для аутентификации и отправки запросов.
А так-же контекстный менеджер логирования запросов и декоратор для аутентификации запросов в функциях.
Логирует запросы и ошибки.
"""
from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from iiko_api.core.config.logging_config import get_logger
from iiko_api.exceptions import IikoConnectionError, IikoTimeoutError

logger = get_logger(__name__)

LOGIN_ENDPOINT = "/resto/api/auth"
LOGOUT_ENDPOINT = "/resto/api/logout"

DEFAULT_SENSITIVE_PARAMS = (
    "login",
    "pass",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "key",
)


def sanitize_url(url: str | None, sensitive_params: list[str] | None = None) -> str:
    """Удаляет чувствительные параметры из URL перед логированием."""
    if not url:
        return ""

    if sensitive_params is None:
        sensitive_params = list(DEFAULT_SENSITIVE_PARAMS)

    try:
        parsed = urlparse(str(url))
        if not parsed.query:
            return str(url)

        query_params = parse_qs(parsed.query, keep_blank_values=True)
        for param in sensitive_params:
            query_params.pop(param, None)

        if not query_params:
            return urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params, "", parsed.fragment)
            )

        new_query = urlencode(query_params, doseq=True)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )
    except Exception:
        # Never fall back to the raw URL (may contain credentials).
        return "<unparseable-url>"


class BaseClient:
    """Базовый класс для работы с API iiko."""

    def __init__(
        self,
        base_url: str,
        login: str,
        hash_password: str,
        timeout: float = 30.0,
        *,
        log_bodies: bool = False,
    ):
        self.base_url = base_url
        self.secret = hash_password
        self.username = login
        self.timeout = timeout
        self.log_bodies = log_bodies
        self.session = requests.Session()

    def _log_exchange(self, response: Response, *, level: str = "debug") -> None:
        request = response.request
        message = (
            f"Request URL: {sanitize_url(request.url)}\n"
            f"  Request Method: {request.method}\n"
            f"  Status: {response.status_code}"
        )
        if self.log_bodies:
            message += (
                f"\n  Request Body: {request.body}\n"
                f"  Response Body: {response.text}"
            )
        log_fn = logger.debug if level == "debug" else logger.error
        log_fn(message)

    @staticmethod
    def _handle_request_errors(func: Callable) -> Callable:
        def wrapper(self: BaseClient, *args: Any, **kwargs: Any):
            try:
                response: Response = func(self, *args, **kwargs)
                response.raise_for_status()
                self._log_exchange(response, level="debug")
                return response
            except HTTPError as http_error:
                logger.error(
                    "HTTP error: %s - Status code: %s",
                    http_error,
                    http_error.response.status_code if http_error.response is not None else "?",
                )
                if http_error.response is not None:
                    self._log_exchange(http_error.response, level="debug")
                raise
            except ConnectionError as connection_error:
                logger.error("Connection error: %s", connection_error)
                raise IikoConnectionError(
                    f"Ошибка подключения к API iiko: {connection_error}",
                    original_exception=connection_error,
                ) from connection_error
            except Timeout as timeout_error:
                logger.error("Timeout error: %s", timeout_error)
                raise IikoTimeoutError(
                    f"Превышено время ожидания ответа от API iiko: {timeout_error}",
                    original_exception=timeout_error,
                ) from timeout_error
            except RequestException as request_error:
                logger.error("Request error: %s", request_error)
                raise
            except Exception as e:
                logger.error("Unexpected error: %s", e)
                raise

        return wrapper

    @_handle_request_errors
    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Response:
        return self.session.get(self.base_url + endpoint, params=params, timeout=self.timeout)

    @_handle_request_errors
    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        *,
        json: dict[str, Any] | None = None,
    ) -> Response:
        return self.session.post(
            self.base_url + endpoint,
            data=data,
            json=json,
            headers=headers,
            timeout=self.timeout,
        )

    def login(self) -> str:
        params = {"login": self.username, "pass": self.secret}
        response = self.get(endpoint=LOGIN_ENDPOINT, params=params)
        if response.ok:
            logger.info("Аутентификация прошла успешно")
            return response.text
        logger.error("Ошибка аутентификации")
        return ""

    def logout(self) -> None:
        response = self.get(endpoint=LOGOUT_ENDPOINT)
        if response.ok:
            logger.info("Токен аутентификации отменен")
        else:
            logger.error("Ошибка отмены аутентификации")

    @contextlib.contextmanager
    def auth(self):
        self.login()
        try:
            yield
        finally:
            self.logout()

    def with_auth(self, func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with self.auth():
                return func(*args, **kwargs)

        return wrapper
