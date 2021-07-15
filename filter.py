import operator
from enum import Enum

from sqlalchemy import Table, Column, and_


class Operator(Enum):
    """
    Supported operators for filter
    """
    eq = "=="
    gt = ">"
    lt = "<"
    ge = ">="
    le = "<="


class Filter:

    def __init__(self, key: Column, value, op="eq"):
        """
        Filter - sqlalchemy filter condition
        Args:
            key (Column): sqlalchemy column
            value: value for the filter
            op: operator
                Currently Supported Operators:
                    - "eq"
                    - "gt"
                    - "lt"
                    - "ge"
                    - "le"
        """
        self.key = key
        self.value = key.type.python_type(value)
        self.op = op

    def __str__(self):
        """str representation of the condition"""
        value = self.value
        if not isinstance(self.value, int):
            value = f"'{self.value}'"
        return f"{self.key} {Operator[self.op].value} {value}"

    @property
    def condition(self):
        """Sqlalchemy filter condition"""
        return getattr(operator, self.op)(self.key, self.value)


class Filters:
    def __init__(self, table: Table, filters: dict):
        """
        Filters create a sqlalchemy filters. Currently all the parameters are "And" aggregated.

        Args:
            table (Table): SqlAlchemy table object
            filters (dict):
                key - column names suffixed which operator
                    eg. id__eq => apply "==" on column 'id'
                        temp__gt => apply ">" on column 'temp'
                    Currently Supported Operators:
                    - "eq" => "=="
                    - "gt" => ">"
                    - "lt" => "<"
                    - "ge" => ">="
                    - "le" => "<="

                value - value for the column that should be applied for the filter
        """
        self.filters_dict = filters
        self.table = table

    def __str__(self):
        """string representation of filters"""
        return " and ".join([str(filt) for filt in self.filters])

    @property
    def filters(self):
        """list of query filters"""
        query_filters = []
        for key, value in self.filters_dict.items():
            if len(key.rsplit("__", 1)) == 2:
                column_name, op = key.rsplit("__", 1)
            else:
                column_name = key
                op = "eq"
            query_filters.append(Filter(self.table.columns[column_name], value, op))
        return query_filters

    @property
    def condition(self):
        """Sqlalchemy filter condition"""
        cond_list = [filt.condition for filt in self.filters]
        return and_(*cond_list)
