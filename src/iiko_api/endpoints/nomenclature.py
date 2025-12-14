import json

from requests import Response

from iiko_api.core import BaseClient
from iiko_api.exceptions import IikoAPIError
from iiko_api.models.models import Product


class NomenclatureEndpoints:
    """
    Класс предоставляющий методы для работы с номенклатурой
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_nomenclature_list(self,
                              nums: list[str] | None = None,
                              ids: list[str] | None = None,
                              types: list[str] | None = None,
                              category_ids: list[str] | None = None,
                              parent_ids: list[str] | None = None,
                              include_deleted: bool = False,
                              ) -> list[dict]:
        """
        Получение списка элементов номенклатуры, по артикулу, по id, по типу элемента номенклатуры, по категории продукта и по родительской группе.

        :param include_deleted: включать ли удаленные элементы номенклатуры
        :param types: список типов элементов номенклатуры,
         по которым необходимо отфильтровать список элементов номенклатуры, если None - получить все
        :param nums: список артикулов, по которым необходимо отфильтровать список элементов, если None - получить все
        :param ids: список id, по которым необходимо отфильтровать список, если None - получить все
        :param category_ids: список категорий, по которым необходимо отфильтровать список, если None - получить все
        :param parent_ids: список родительских групп, по которым необходимо отфильтровать список, если None - получить все 
        :return: список словарей, где каждый словарь представляет элемент номенклатуры
        :raises ValueError: если ответ API не является валидным JSON
        """
        url = "/resto/api/v2/entities/products/list"
        params = {}
        
        if include_deleted:
            params["includeDeleted"] = "true"
        
        if nums:
            params["nums"] = nums
        if ids:
            params["ids"] = ids
        if types:
            params["types"] = types
        if category_ids:
            params["categoryIds"] = category_ids
        if parent_ids:
            params["parentIds"] = parent_ids
        
        # Выполнение GET-запроса к API, возвращающего данные об элементах номенклатуры
        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.get(url, params=params if params else None)
        
        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e

    def get_nomenclature_groups(
            self, ids: list[str] | None = None,
            parent_ids: list[str] | None = None,
            nums: list[str] | None = None,
            include_deleted: bool = False,
    ) -> list[dict]:
        """
        Получение списка групп номенклатуры

        :param include_deleted: включать ли удаленные группы номенклатуры
        :param ids: список id групп номенклатуры, по которым необходимо получить список, если None - получить все
        :param parent_ids: список id родительских групп номенклатуры, по которым необходимо получить список,
         если None - получить все
        :param nums: список артикулов групп номенклатуры, по которым необходимо получить список,
         если None - получить все

        :return: список словарей, где каждый словарь представляет группу номенклатуры
        :raises ValueError: если ответ API не является валидным JSON
        """
        url = "/resto/api/v2/entities/products/group/list"
        params = {}
        
        if include_deleted:
            params["includeDeleted"] = "true"
        
        if ids:
            params["ids"] = ids
        if parent_ids:
            params["parentIds"] = parent_ids
        if nums:
            params["nums"] = nums
        
        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        result: Response = self.client.get(url, params=params if params else None)
        
        try:
            return result.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e

    def import_product(self, product: Product) -> dict:
        """
        Импорт элемента номенклатуры
        
        :param product: Объект Product с данными элемента номенклатуры
        :return: Словарь с результатом импорта (содержит созданный продукт)
        :raises IikoAPIError: если API вернул ошибку (result != SUCCESS или неожиданный формат ответа)
        :raises ValueError: если ответ API не является валидным JSON
        """
        url = "/resto/api/v2/entities/products/save"
        headers = {"Content-Type": "application/json"}
        
        # Выполнение POST-запроса к API для импорта элемента номенклатуры
        result: Response = self.client.post(
            endpoint=url, 
            data=product.model_dump_json(exclude_none=True), 
            headers=headers
        )
        
        # Безопасный парсинг JSON ответа
        try:
            response_data = result.json()
        except (json.JSONDecodeError, ValueError) as e:
            # Если ответ - не JSON (например, просто строка)
            raise ValueError(
                f"API вернул невалидный JSON. Ответ: {result.text[:200]}"
            ) from e
        
        # Проверяем, что ответ - словарь (не список и не строка)
        if not isinstance(response_data, dict):
            raise IikoAPIError(
                f"API вернул неожиданный формат ответа (ожидался dict, получен {type(response_data).__name__}): {response_data}"
            )
        
        # API возвращает структуру с полями result, errors, response
        # response содержит созданный продукт
        result_status = response_data.get("result")
        
        if result_status == "SUCCESS":
            response_result = response_data.get("response")
            if response_result is None:
                # Если response отсутствует, возвращаем весь ответ
                return response_data
            return response_result
        elif result_status == "ERROR":
            # Бизнес-ошибка API: HTTP 200, но операция не выполнена
            errors = response_data.get("errors", [])
            # Безопасная обработка errors - может быть не списком
            if not isinstance(errors, list):
                errors = []
            
            error_messages = [
                f"{err.get('code', 'UNKNOWN')}: {err.get('value', '')}" 
                for err in errors 
                if isinstance(err, dict)
            ]
            error_message = "Ошибка при импорте продукта"
            if error_messages:
                error_message += f". Ошибки: {', '.join(error_messages)}"
            else:
                error_message += f". Статус: {result_status}"
            
            raise IikoAPIError(error_message, errors=errors)
        else:
            # Неожиданный статус (не SUCCESS и не ERROR)
            raise IikoAPIError(
                f"API вернул неожиданный статус результата: {result_status}. "
                f"Полный ответ: {response_data}"
            )
