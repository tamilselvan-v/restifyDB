from sqlalchemy import MetaData

from config import ConfigReader
from connection import DBConnection


config = ConfigReader(filepath="sample.json").config
db_connection = DBConnection(**config["connection_params"])


print(users_table.__dict__)
with db_connection.session_scope() as session:
    print(session.query(users_table).all())
