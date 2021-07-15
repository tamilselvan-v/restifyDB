import operator
from enum import Enum

from sqlalchemy import Table

class Filter:

    def __init__(self, key, value, op="=="):
        self.key = key
        self.value = key.type.python_type(value)
        self.op = op

    def __str__(self):
        return f"{self.key} {self.op} {self.value}"

    @property
    def filter_condition(self):
        return getattr(operator, self.op)(self.key, self.value)


class Filters:
    def __init__(self, table: Table, filters: dict):
        self.condition = None
        for key, value in filters.items():
            if len(key.rsplit("__", 1)) == 2:
                column_name, op = key.rsplit("__", 1)
            else:
                column_name = key
                op = "eq"
            query = Filter(table.columns[column_name], value, op).filter_condition
            if self.condition:
                self.condition = query & self.condition
            else:
                self.condition = query

    @property
    def filter_condition(self):
        return self.condition
