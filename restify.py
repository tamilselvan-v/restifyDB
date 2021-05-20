from sqlalchemy import MetaData

from config import ConfigReader
from connection import DBConnection
from flask import Flask, url_for

from db_service import DBService
from helpers import object_as_dict

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

config = ConfigReader(filepath="sample.json").config
db_connection = DBConnection(**config["connection_params"])

db_service = DBService(db_connection=db_connection)


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route("/tables", methods=["GET"])
def fetch_all_tables():
    meta = MetaData()
    meta.reflect(bind=db_connection.engine)
    return {"tables": [table for table in meta.tables.keys()]}

@app.route("/tables/<table_name>", methods=["GET"])
def fetch_all_rows(table_name: str):
    meta = MetaData()
    meta.reflect(bind=db_connection.engine)
    table = meta.tables[table_name]
    with db_connection.session_scope() as session:
        rows = session.query(table).all()

    result = []
    for row in rows:
        row_json = {field: str(getattr(row, field, "")) for field in row._fields}
        result.append(row_json)
    return {"rows": result}


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        links.append((str(rule), rule.endpoint, str(rule.methods)))
    return {"routes": links}


if __name__ == "__main__":
    app.run(port=9567)
