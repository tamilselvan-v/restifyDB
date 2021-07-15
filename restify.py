from logging import getLogger

from sqlalchemy import MetaData

from config import ConfigReader
from connection import DBConnection
from flask import Flask, request

from db_service import DBService

logger = getLogger(__name__)

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
    page_no = int(request.args.get("pageNo", 1))
    rows_per_page = int(request.args.get("maxRows", 100))
    offset = (page_no - 1) * rows_per_page
    with db_connection.session_scope() as session:
        rows = session.query(table).offset(offset).limit(rows_per_page).all()

    result = []
    for row in rows:
        row_json = {field: str(getattr(row, field, "")) for field in row._fields}
        result.append(row_json)
    return {"rows": result}


@app.route("/tables/<table_name>", methods=["POST"])
def insert_to_table(table_name: str):
    meta = MetaData()
    meta.reflect(bind=db_connection.engine)
    table = meta.tables[table_name]
    data = request.json
    insert = table.insert().values(**data)
    try:
        with db_connection.session_scope() as session:
            session.execute(insert)
    except Exception as e:
        logger.exception(f"inserting the record into {table_name} failed")
        return {"error": str(e)}
    return {"status": "success"}


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        links.append((str(rule), rule.endpoint, str(rule.methods)))
    return {"routes": links}


if __name__ == "__main__":
    app.run(port=9567)
