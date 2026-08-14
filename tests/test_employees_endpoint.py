"""Тесты для EmployeesEndpoints."""

from unittest.mock import Mock

from iiko_api.endpoints.employees import EmployeesEndpoints

ONE_EMPLOYEE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<employees>
  <employee>
    <id>aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee</id>
    <name>Иванов</name>
    <deleted>true</deleted>
  </employee>
</employees>
"""


def _xml_response(text: str) -> Mock:
    response = Mock()
    response.status_code = 200
    response.ok = True
    response.text = text
    return response


def test_get_employees_default_omits_include_deleted(mock_base_client) -> None:
    mock_base_client.get.return_value = _xml_response(ONE_EMPLOYEE_XML)
    endpoint = EmployeesEndpoints(mock_base_client)

    rows = endpoint.get_employees()

    mock_base_client.get.assert_called_once_with("/resto/api/employees/", params=None)
    assert len(rows) == 1
    assert rows[0]["name"] == "Иванов"


def test_get_employees_include_deleted_passes_rms_flag(mock_base_client) -> None:
    mock_base_client.get.return_value = _xml_response(ONE_EMPLOYEE_XML)
    endpoint = EmployeesEndpoints(mock_base_client)

    rows = endpoint.get_employees(include_deleted=True)

    mock_base_client.get.assert_called_once_with(
        "/resto/api/employees/",
        params={"includeDeleted": "true"},
    )
    assert len(rows) == 1
    assert rows[0]["name"] == "Иванов"
    assert rows[0]["deleted"] == "true"
