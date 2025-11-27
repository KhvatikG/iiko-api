from requests import Response
import logging

from iiko_api.core import BaseClient
from iiko_api.models.models import AssemblyChart

logger = logging.getLogger(__name__)


class AssemblyChartsEndpoints:
    """
    Класс, предоставляющий методы для работы с техкартами.
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_all_assembly_charts(
            self,
            date_from: str,
            date_to: str = None,
            include_prepared_charts: bool = True,
            include_deleted_products: bool = False
    ) -> dict | None:
        """
        Получение всех техкарт.

        :param date_from: Дата начала периода в формате "ГГГГ-ММ-ДД"
        :param date_to: Дата окончания периода в формате "ГГГГ-ММ-ДД" (необязательный параметр)
        :param include_prepared_charts: Разложить ли вложенные техкарты до конечных ингридиентов (по умолчанию True)
        :param include_deleted_products: Включать ли техкарты с удаленными продуктами (по умолчанию False)
        :return: Словарь:
            Ключи:
                assemblyCharts - Список исходных технологических карт,
                интервал действия которых пересекает запрошенный интервал.

                preparedCharts - Список разложенных до ингредиентов технологических карт,
                интервал действия которых пересекает запрошенный интервал.
        """
        url = "/resto/api/v2/assemblyCharts/getAll"
        url += "?"

        if date_from:
            url += f"dateFrom={date_from}&"

        if date_to:
            url += f"dateTo={date_to}&"

        if include_prepared_charts:
            url += f"includePreparedCharts={include_prepared_charts}&"

        if include_deleted_products:
            url += f"includeDeletedProducts={include_deleted_products}&"

        # Получение данных
        result: Response = self.client.get(url)

        if result.status_code == 200:
            return result.json()
        else:
            return None

    def save_assembly_chart(self, assembly_chart: AssemblyChart) -> dict | None:
        """
        Сохранение технологической карты.
        
        :param assembly_chart: Объект AssemblyChart с данными технологической карты
        :return: Словарь с полной технологической картой, созданной на сервере, или None в случае ошибки.
                 Возвращаемая техкарта содержит все поля из запроса плюс дополнительные поля от сервера:
                 - id: UUID созданной техкарты
                 - items[].id: UUID созданных ингредиентов
                 - items[].packageCount: количество фасовок (если применимо)
                 и другие поля, возвращаемые API
        """
        url = "/resto/api/v2/assemblyCharts/save"
        headers = {"Content-Type": "application/json"}
        
        # Выполнение POST-запроса к API для сохранения технологической карты
        result: Response = self.client.post(
            endpoint=url,
            data=assembly_chart.model_dump_json(exclude_none=True),
            headers=headers
        )
        
        if result.status_code == 200:
            response_data = result.json()
            # API возвращает структуру с полями result, errors, response
            # response содержит полную созданную техкарту со всеми полями от сервера
            if response_data.get("result") == "SUCCESS":
                return response_data.get("response")
            else:
                errors = response_data.get("errors", [])
                error_messages = [f"{err.get('code', 'UNKNOWN')}: {err.get('value', '')}" for err in errors]
                logger.error(f"Ошибка при сохранении техкарты. Статус: {response_data.get('result')}")
                logger.error(f"Ошибки API: {', '.join(error_messages)}")
                logger.debug(f"Полный ответ API: {response_data}")
                return None
        else:
            logger.error(f"HTTP ошибка при сохранении техкарты. Статус код: {result.status_code}")
            logger.debug(f"Текст ответа: {result.text}")
            return None
