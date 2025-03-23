from datetime import datetime
from requests import Response

import xmltodict

from iiko_api.core import BaseClient


class StoresEndpoints:
    """
    Класс, предоставляющий методы для работы со складами
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_stores(self, auto_login=True) -> dict | None:
        """
        Метод для получения списка складов

        :param auto_login: Если True, то метод автоматически выполняет вход в систему и выход из нее
        """
        url = "/resto/api/corporation/stores"

        if auto_login:
            self.client.login()

        xml_data = self.client.get(url)

        if auto_login:
            self.client.logout()

        if xml_data.status_code != 200:
            return None

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        return dict_data["corporateItemDtoes"]["corporateItemDto"]

    def get_stores_balance(self, timestamp: str = "now", auto_login=True):
        """
        Метод для получения остатков на складах

        :param auto_login: Если True, то метод автоматически выполняет вход в систему и выход из нее
        :param timestamp: Время, на которое необходимо получить остатки(можно указать "now")
        """
        url = "/resto/api/v2/reports/balance/stores"

        if auto_login:
            self.client.login()

        if timestamp != "now":
            url += "?timestamp=" + timestamp
        else:
            url += f"?timestamp={datetime.now().strftime('%Y-%m-%d')}"

        result: Response = self.client.get(url).json()

        if auto_login:
            self.client.logout()

        if result.status_code == 200:
            return result.json()
        else:
            return None
