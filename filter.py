import operator
from enum import Enum

from sqlalchemy import Table, Column, and_


class Filter:

    def __init__(self, key: Column, value, op="=="):
        self.key = key
        self.value = key.type.python_type(value)
        self.op = op

    def __str__(self):
        return f"{self.key} {self.op} {self.value}"

    @property
    def condition(self):
        return getattr(operator, self.op)(self.key, self.value)


class Filters:
    def __init__(self, table: Table, filters: dict):
        self.filters = filters
        self.table = table

    @property
    def condition(self):
        filters = []
        for key, value in self.filters.items():
            if len(key.rsplit("__", 1)) == 2:
                column_name, op = key.rsplit("__", 1)
            else:
                column_name = key
                op = "eq"
            filters.append(Filter(self.table.columns[column_name], value, op).condition)
        return and_(*filters)
