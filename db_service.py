from typing import List

from sqlalchemy import MetaData


class DBService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_all_rows(self, table_name: str) -> List[dict]:
        """
        Get all rows in a table
        Args:
            table_name (str): table name

        Returns:
            List[dict]
        """
        meta = MetaData()
        meta.reflect(bind=self.db_connection.engine)
        table = meta.tables[table_name]

        with self.db_connection.session_scope() as session:
            result = session.query(table).all()

        return result
