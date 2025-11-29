"""
Модуль для работы с API iiko
Содержит Базовый класс для работы с API iiko.
Включающий методы: get, post
Методы для аутентификации и отправки запросов.
А так-же контекстный менеджер логирования запросов и декоратор для аутентификации запросов в функциях.
Логирует запросы и ошибки.
"""
import contextlib
from typing import Callable, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests
from requests import Response
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from iiko_api.core.config.logging_config import get_logger

logger = get_logger(__name__)

LOGIN_ENDPOINT = "/resto/api/auth"
LOGOUT_ENDPOINT = "/resto/api/logout"


def sanitize_url(url: str | None, sensitive_params: list[str] = None) -> str:
    """
    Удаляет чувствительные параметры из URL перед логированием
    
    :param url: URL для очистки (может быть None)
    :param sensitive_params: список параметров для удаления (по умолчанию: login, pass)
    :return: URL без чувствительных параметров или исходный URL если обработка не удалась
    """
    if not url:
        return str(url) if url is not None else ""
    
    if sensitive_params is None:
        sensitive_params = ["login", "pass"]
    
    try:
        parsed = urlparse(str(url))
        
        # Если нет query параметров, возвращаем как есть
        if not parsed.query:
            return str(url)
        
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        
        # Удаляем чувствительные параметры
        for param in sensitive_params:
            query_params.pop(param, None)
        
        # Если все параметры были удалены, убираем "?" из URL
        if not query_params:
            sanitized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                "",  # пустой query
                parsed.fragment
            ))
        else:
            # Собираем URL обратно с оставшимися параметрами
            new_query = urlencode(query_params, doseq=True)
            sanitized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
        
        return sanitized
    except Exception:
        # В случае любой ошибки возвращаем исходный URL
        # (лучше показать URL с данными, чем сломать логирование)
        return str(url)


class BaseClient:
    """
    Базовый класс для работы с API iiko
    """
    def __init__(self, base_url: str, login: str, hash_password: str):
        """
        Инициализация клиента API iiko
        :param base_url: базовый URL-адрес API
        :param login: имя пользователя
        :param hash_password: хэш пароля
        """
        self.base_url = base_url
        self.secret = hash_password
        self.username = login
        self.session = requests.Session()

    @staticmethod
    def _handle_request_errors(func: Callable) -> Callable:
        """
        Декоратор для обработки ошибок HTTP запросов
        :param func: Функция для обработки ошибок
        :return:
        """

        def wrapper(*args, **kwargs):
            try:
                response: Response = func(*args, **kwargs)
                response.raise_for_status()
                logger.debug(f"Request URL: {sanitize_url(response.request.url)}\n"
                            f"  Request Method: {response.request.method}\n"
                            f"  Request Body: {response.request.body}\n"
                            f"  Response Body: {response.text}\n"
                             )
                return response
            except HTTPError as http_error:
                logger.error(f"HTTP error: {http_error} - Status code: {http_error.response.status_code}")
                logger.debug(f"\n  Request URL: {sanitize_url(http_error.response.url)}\n"
                            f"  Request Method: {http_error.response.request.method}\n"
                            f"  Request Headers: {http_error.response.request.headers}\n"
                            f"  Request Body: {http_error.response.request.body}\n"
                            f"  Response Headers: {http_error.response.headers}\n"
                            f"  Response Body: {http_error.response.text}\n"
                            )
                raise
            except ConnectionError as connection_error:
                logger.error(f"Connection error: {connection_error}")
                raise
            except Timeout as timeout_error:
                logger.error(f"Timeout error: {timeout_error}")
                raise
            except RequestException as request_error:
                logger.error(f"Request error: {request_error}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

        return wrapper

    @_handle_request_errors
    def get(self, endpoint: str, params: dict[str, Any] = None) -> Response:
        """
        Метод для выполнения GET запроса
        :param endpoint: конечная точка API
        :param params: параметры запроса
        :return: ответ сервера
        """
        return self.session.get(self.base_url + endpoint, params=params)

    @_handle_request_errors
    def post(self, endpoint: str, data: dict[str, Any] = None, headers: dict[str, Any] = None) -> Response:
        """
        Метод для выполнения POST запроса
        :param headers: Заголовки запроса
        :param endpoint: конечная точка API
        :param data: данные запроса
        :return: ответ сервера
        """
        return self.session.post(self.base_url + endpoint, data=data, headers=headers)

    def login(self) -> str:
        """
        Метод для аутентификации, токен сохраняется в сессии
        :return:
        """
        params = {"login": self.username, "pass": self.secret}
        response = self.get(endpoint=LOGIN_ENDPOINT, params=params)
        if response.ok:
            logger.info("Аутентификация прошла успешно")
            return response.text
        else:
            logger.error("Ошибка аутентификации")
            logger.debug(f"Ответ: {response.text}")

    def logout(self) -> None:
        """
        Метод для отмены аутентификации, токен удаляется из сессии
        :return:
        """
        response = self.get(endpoint=LOGOUT_ENDPOINT)
        if response.ok:
            logger.info("Токен аутентификации отменен")
        else:
            logger.error("Ошибка отмены аутентификации")
            logger.debug(f"Ответ: {response.text}")

    @contextlib.contextmanager
    def auth(self) -> None:
        """
        Контекстный менеджер для аутентификации запросов
        """
        self.login()
        try:
            yield
        finally:
            self.logout()

    def with_auth(self, func: Callable) -> Callable:
        """
        Декоратор для выполнения функции с аутентификацией
        """
        def wrapper(*args, **kwargs) -> Any:
            with self.auth():
                return func(*args, **kwargs)
        return wrapper
