from datetime import date, datetime

import xmltodict

from iiko_api.core import BaseClient


class ReportsEndpoints:
    """
    Класс, предоставляющий методы для работы с отчетами по API
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_sales_report(
            self, date_from: datetime, date_to: datetime, department_id: str, date_aggregation: bool = True
    ) -> dict[date, float] | list[dict]:
        """
        Получение отчета по продажам за период.
        Возвращает словарь, где ключ это дата, а значение это выручка, если date_aggregation=True
        Если date_aggregation=False, то отчет будет списком словарей с ключами date и value.

        :param department_id: ID отдела
        :param date_from: Начало периода
        :param date_to: Конец периода включается в отчет
        :param date_aggregation: Если True, то отчет будет агрегирован по дням, иначе будет соответствовать выводу iiko.
        :return: Словарь, где ключ это дата, а значение это выручка, или список словарей
        :raises ValueError: если department_id пустой, date_from > date_to, XML не может быть распарсен или структура данных неожиданная
        """
        if not department_id:
            raise ValueError("department_id не может быть пустым")
        
        if date_from > date_to:
            raise ValueError("date_from должен быть меньше или равен date_to")

        date_format = '%d.%m.%Y'
        date_from_str = datetime.strftime(date_from, date_format)
        date_to_str = datetime.strftime(date_to, date_format)

        endpoint = '/resto/api/reports/sales'

        params = {
            'department': department_id,
            'dateFrom': date_from_str,
            'dateTo': date_to_str,
            'allRevenue': 'false'
        }

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        xml_data = self.client.get(endpoint=endpoint, params=params)

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        try:
            day_dish_values = dict_data.get('dayDishValues', {})
            day_dish_value = day_dish_values.get('dayDishValue')
            
            # Если day_dish_value - None, возвращаем пустой результат
            if day_dish_value is None:
                return {} if date_aggregation else []
            
            # Если day_dish_value - один элемент (не список), преобразуем в список
            if isinstance(day_dish_value, dict):
                day_dish_value = [day_dish_value]
            
            if date_aggregation:
                agg_dict_data: dict[date, float] = {}
                if isinstance(day_dish_value, list):
                    for day in day_dish_value:
                        day_date = datetime.strptime(day['date'], date_format).date()
                        # Преобразуем value в float
                        value = float(day.get('value', 0))
                        agg_dict_data[day_date] = value
                return agg_dict_data
            
            # Если date_aggregation=False, возвращаем список
            if isinstance(day_dish_value, list):
                return day_dish_value
            return [day_dish_value]
        except (KeyError, AttributeError, ValueError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа или ошибка обработки данных. "
                f"Ожидалась структура dayDishValues/dayDishValue. Ответ: {xml_data.text[:200]}"
            ) from e
