from .core.base_client import BaseClient
from .endpoints.employees import EmployeesEndpoints, RolesEndpoints, ReportsEndpoints
from .endpoints.nomenclature import NomenclatureEndpoints
from .endpoints.olap import OLAP
from .endpoints.orders import OrdersEndpoints
from .endpoints.assembly_charts import AssemblyChartsEndpoints
from .endpoints.stores import StoresEndpoints


class IikoApi:
    def __init__(self, base_url: str, login: str, hash_password: str):
        # Инициализируем базовый клиент
        self.client = BaseClient(base_url, login, hash_password)
        self.with_authorization = self.client.with_auth
        self.auth_context = self.client.auth

        # Инициализируем эндпоинты, передавая клиент в конструктор каждого из них
        self.employees = EmployeesEndpoints(self.client)
        self.roles = RolesEndpoints(self.client)
        self.reports = ReportsEndpoints(self.client)
        self.nomenclature = NomenclatureEndpoints(self.client)
        self.orders = OrdersEndpoints(self.client)
        self.assembly_charts = AssemblyChartsEndpoints(self.client)
        self.stores = StoresEndpoints(self.client)
        self.olap = OLAP(self.client)

