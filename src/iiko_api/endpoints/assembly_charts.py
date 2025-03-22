import json

from iiko_api.core import BaseClient


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
    ) -> list[dict]:
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
        # Авторизация
        self.client.login()

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
        data = self.client.get(url)

        # Отпускаем авторизацию
        self.client.logout()

        data = json.loads(data.text)

        return data
