from uuid import UUID
from datetime import datetime

from requests.exceptions import HTTPError

from iiko_api.core import BaseClient
from iiko_api.exceptions import EmployeeNotFoundError, RoleNotFoundError
import xmltodict


class EmployeesEndpoints:
    """
    Класс, предоставляющий методы для работы с сотрудниками
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_employees(self) -> list[dict]:
        """
        Получение списка всех сотрудников

        :return: список словарей, где каждый словарь представляет сотрудника
        :raises ValueError: если XML не может быть распарсен или структура данных неожиданная
        """
        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        xml_data = self.client.get('/resto/api/employees/')

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        # Безопасное извлечение данных из структуры XML
        try:
            employees_data = dict_data.get('employees', {})
            employees = employees_data.get('employee')
            
            # Если employees - None, возвращаем пустой список
            if employees is None:
                return []
            
            # Если employees - один элемент (не список), преобразуем в список
            if isinstance(employees, dict):
                return [employees]
            
            # Если employees - список, возвращаем как есть
            if isinstance(employees, list):
                return employees
            
            raise ValueError(f"Неожиданная структура данных: {type(employees)}")
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура employees/employee. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e

    def get_employee_by_id(self, employee_id: UUID) -> dict:
        """
        Получение данных о сотруднике по его ID

        :param employee_id: UUID сотрудника
        :return: словарь, где каждый ключ представляет поле сотрудника, а значение - его значение
        :raises EmployeeNotFoundError: если сотрудник не найден (HTTP 404)
        :raises ValueError: если XML не может быть распарсен или структура данных неожиданная
        """
        try:
            xml_data = self.client.get(f'/resto/api/employees/byId/{employee_id}')
        except HTTPError as e:
            # Обработка 404 ошибки - сотрудник не найден
            if e.response.status_code == 404:
                server_message = e.response.text.strip() if e.response.text else None
                raise EmployeeNotFoundError(str(employee_id), server_message) from e
            # Для других HTTP ошибок пробрасываем дальше
            raise

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        try:
            employee_data = dict_data.get('employee')
            if employee_data is None:
                raise ValueError(
                    f"Сотрудник с ID {employee_id} не найден. Ответ: {xml_data.text[:200]}"
                )
            
            # Нормализация departmentCodes
            if employee_data.get('departmentCodes') and not isinstance(employee_data.get('departmentCodes'), list):
                employee_data['departmentCodes'] = [employee_data.get('departmentCodes')]
            else:
                employee_data['departmentCodes'] = employee_data.get('departmentCodes', [])

            return employee_data
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура employee. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e

    def get_employees_by_department(self, department_code: str) -> list[dict]:
        """
        Получение списка сотрудников по коду отдела

        :param department_code: Код отдела
        :return: список словарей, где каждый словарь представляет сотрудника привязанного к отделу
        :raises ValueError: если department_code пустой, XML не может быть распарсен или структура данных неожиданная
        """
        if not department_code:
            raise ValueError("department_code не может быть пустым")

        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        xml_data = self.client.get(f'/resto/api/employees/byDepartment/{department_code}')

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        try:
            employees_data = dict_data.get('employees', {})
            employees_list = employees_data.get('employee', [])
            
            # Если employees_list - None, возвращаем пустой список
            if employees_list is None:
                return []
            
            # Если employees_list - один элемент (не список), преобразуем в список
            if isinstance(employees_list, dict):
                employees_list = [employees_list]
            
            # Нормализация departmentCodes для каждого сотрудника
            employees = []
            for employee in employees_list:
                if employee.get('departmentCodes') and not isinstance(employee.get('departmentCodes'), list):
                    employee['departmentCodes'] = [employee.get('departmentCodes')]
                else:
                    employee['departmentCodes'] = employee.get('departmentCodes', [])
                employees.append(employee)

            return employees
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура employees/employee. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e

    def get_attendances_for_department(
            self,
            department_code: str,
            date_from: datetime,
            date_to: datetime
    ) -> list[dict]:
        """
        Получение явок сотрудников по отделу за период.

        :param department_code: Код отдела
        :param date_from: Начало периода
        :param date_to: Конец периода, включительно
        :return: Список словарей, где каждый словарь представляет явку
        :raises ValueError: если department_code пустой, date_from > date_to, XML не может быть распарсен или структура данных неожиданная
        """
        if not department_code:
            raise ValueError("department_code не может быть пустым")
        
        if date_from > date_to:
            raise ValueError("date_from должен быть меньше или равен date_to")

        date_from_str = datetime.strftime(date_from, '%Y-%m-%d')
        date_to_str = datetime.strftime(date_to, '%Y-%m-%d')

        endpoint = f'/resto/api/employees/attendance/byDepartment/{department_code}'

        params = {
            'from': date_from_str,
            'to': date_to_str
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
            attendances_data = dict_data.get('attendances', {})
            attendances = attendances_data.get('attendance')
            
            # Если attendances - None, возвращаем пустой список
            if attendances is None:
                return []
            
            # Если attendances - один элемент (не список), преобразуем в список
            if isinstance(attendances, dict):
                return [attendances]
            
            # Если attendances - список, возвращаем как есть
            if isinstance(attendances, list):
                return attendances
            
            raise ValueError(f"Неожиданная структура данных: {type(attendances)}")
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура attendances/attendance. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e


class RolesEndpoints:
    """
    Класс, предоставляющий методы для работы с ролями сотрудников по API
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_roles(self) -> list[dict]:
        """
        Получение списка всех ролей

        :return: Список словарей, где каждый словарь представляет роль
        :raises ValueError: если XML не может быть распарсен или структура данных неожиданная
        """
        # Декоратор _handle_request_errors уже обработал ошибки (status >= 400)
        xml_data = self.client.get('/resto/api/employees/roles/')

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        try:
            roles_data = dict_data.get('employeeRoles', {})
            roles = roles_data.get('role')
            
            # Если roles - None, возвращаем пустой список
            if roles is None:
                return []
            
            # Если roles - один элемент (не список), преобразуем в список
            if isinstance(roles, dict):
                return [roles]
            
            # Если roles - список, возвращаем как есть
            if isinstance(roles, list):
                return roles
            
            raise ValueError(f"Неожиданная структура данных: {type(roles)}")
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура employeeRoles/role. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e

    def get_role_by_id(self, role_id: str) -> dict:
        """
        Получение роли по ID

        :param role_id: ID роли
        :return: Словарь, где каждый ключ представляет поле роли, а значение - его значение
        :raises RoleNotFoundError: если роль не найдена (HTTP 404)
        :raises ValueError: если role_id пустой, XML не может быть распарсен или структура данных неожиданная
        """
        if not role_id:
            raise ValueError("role_id не может быть пустым")

        try:
            xml_data = self.client.get(f'/resto/api/employees/roles/byId/{role_id}')
        except HTTPError as e:
            # Обработка 404 ошибки - роль не найдена
            if e.response.status_code == 404:
                server_message = e.response.text.strip() if e.response.text else None
                raise RoleNotFoundError(role_id, server_message) from e
            # Для других HTTP ошибок пробрасываем дальше
            raise

        try:
            # Преобразование XML-данных в словарь
            dict_data = xmltodict.parse(xml_data.text)
        except Exception as e:
            raise ValueError(
                f"Не удалось распарсить XML ответ. Ошибка: {e}. Ответ: {xml_data.text[:200]}"
            ) from e

        try:
            role_data = dict_data.get('role')
            if role_data is None:
                raise ValueError(
                    f"Роль с ID {role_id} не найдена. Ответ: {xml_data.text[:200]}"
                )
            return role_data
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Неожиданная структура XML ответа. Ожидалась структура role. "
                f"Ответ: {xml_data.text[:200]}"
            ) from e
