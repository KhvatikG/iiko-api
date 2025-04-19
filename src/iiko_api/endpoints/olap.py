from uuid import UUID
from datetime import datetime, timedelta
from requests import Response

from iiko_api.core import BaseClient


class OLAP:
    """Класс представляющий методы работы с OLAP отчетами"""

    def __init__(self, client: BaseClient):
        self.client = client

    def get_olap_by_preset_id(
            self,
            preset_id: str,
            date_from: datetime = None,
            date_to: datetime = None,
            auto_login: bool = True
    ) -> dict:
        """
        Получить отчет по ID преднастроенного отчета, дата начала и конца отчета должны отличаться.

        :param preset_id: UUID преднастроенного отчета
        :param date_from: дата начала отчета (включается в отчет)
        :param date_to: дата конца отчета (не включается в отчет)
        :param auto_login: если True, то авторизация будет выполнена автоматически
        :return: словарь с данными отчета
         """

        try:
            UUID(preset_id)
        except ValueError:
            raise TypeError('preset_id должен быть типа UUID')

        if date_from and not isinstance(date_from, datetime):
            raise TypeError('date_from должен быть типа datetime')
        if date_to and not isinstance(date_to, datetime):
            raise TypeError('date_to должен быть типа datetime')
        if date_from and date_to and date_from == date_to:
            raise ValueError('date_from и date_to должны быть разными')
        if date_from and date_to and date_from > date_to:
            raise ValueError('date_from должен быть меньше date_to')

        url = '/resto/api/v2/reports/olap/byPresetId/' + str(preset_id)

        if date_from is None:
            date_from = datetime.now().strftime('%Y-%m-%d')
        else:
            date_from = date_from.strftime('%Y-%m-%d')

        if date_to is None:
            date_to = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            date_to = date_to.strftime('%Y-%m-%d')

        if auto_login:
            self.client.login()

        params = {'dateFrom': date_from, 'dateTo': date_to}

        result: Response = self.client.get(url, params=params)

        self.client.logout()

        result.raise_for_status()

        return result.json()






