from logging import getLogger
from typing import List, Optional

from sqlalchemy import MetaData

from filter import Filters

logger = getLogger(__name__)


class DBService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_all_rows(self, table_name: str,
                     page_no: Optional[int] = 1,
                     max_rows: Optional[int] = 100,
                     filters: Optional[dict] = None
                     ) -> List[dict]:
        """
        Get all rows in a table
        Args:
            filters (dict): dict of fitlers
                Key - <column_name>__<operator> Eg. id__eq
                value - filter value
            max_rows (int): max number of rows per page
            page_no (int): page no for pagination
            table_name (str): table name

        Returns:
            List[dict]
        """
        if not filters:
            filters = {}

        meta = MetaData()
        meta.reflect(bind=self.db_connection.engine)
        table = meta.tables[table_name]
        offset = (page_no - 1) * max_rows
        with self.db_connection.session_scope() as session:
            rows = session.query(table).filter(Filters(table, filters).condition).offset(offset).limit(max_rows).all()

        result = []
        for row in rows:
            row_json = {field: str(getattr(row, field, "")) for field in row._fields}
            result.append(row_json)
        return result

    def fetch_all_tables(self):
        meta = MetaData()
        meta.reflect(bind=self.db_connection.engine)
        return {"tables": [table for table in meta.tables.keys()]}

    def insert_into_table(self, table_name: str, row: dict):
        meta = MetaData()
        meta.reflect(bind=self.db_connection.engine)
        table = meta.tables[table_name]
        insert = table.insert().values(**row)
        with self.db_connection.session_scope() as session:
            session.execute(insert)

    def update_row(self, table_name, filters:dict, values_to_be_updated: dict):
        """
        Update row
        Args:
            table_name:
            filters:
            values_to_be_updated:

        Returns:

        """
        meta = MetaData()
        meta.reflect(bind=self.db_connection.engine)
        table = meta.tables[table_name]
        with self.db_connection.session_scope() as session:
            rows = session.query(table).filter(Filters(table, filters).condition).update(values_to_be_updated)
        return rows
