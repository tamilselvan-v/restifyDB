from logging import getLogger

from flasgger import Swagger
from sqlalchemy import MetaData

from config import ConfigReader
from connection import DBConnection
from flask import Flask, request, jsonify

from db_service import DBService
from filter import Filters

logger = getLogger(__name__)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SWAGGER'] = {
    'title': 'RestifyDB',
    'uiversion': 3
}
swagger = Swagger(app)

config = ConfigReader(filepath="sample.json").config
db_connection = DBConnection(**config["connection_params"])

db_service = DBService(db_connection=db_connection)


@app.route("/tables", methods=["GET"])
def fetch_all_tables():
    meta = MetaData()
    meta.reflect(bind=db_connection.engine)
    return {"tables": [table for table in meta.tables.keys()]}


@app.route("/tables/<table_name>", methods=["GET"])
def fetch_all_rows(table_name: str):
    """
    Return paginated response of all the rows from the table
    ---
    parameters:
        - name: table_name
          in: path
          type: string
          required: true
          description: name of the table
        - name: pageNo
          in: query
          type: string
          required: false
          description: page number for paginated response
          default: 1
        - name: maxRows
          in: query
          type: string
          required: false
          description: max number of rows per page in the response
          default: 100
        - in: query
          name: params
          description: |
            Filter parameters (key=value)
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
          schema:
            type: object
            # If the parameter values are of specific type, e.g. string:
            additionalProperties:
              type: string
            # If the parameter values can be of different types
            # (e.g. string, number, boolean, ...)
            # additionalProperties: true

          # `style: form` and `explode: true` is the default serialization method
          # for query parameters, so these keywords can be omitted
          style: form
          explode: true

    responses:
      200:
        description: A list of rows (may be filtered by args, pageNo, maxRows)
    """
    args = dict(request.args)
    page_no = args.pop("pageNo", 1)
    max_rows = args.pop("maxRows", 100)
    result = db_service.get_all_rows(table_name=table_name, page_no=page_no, max_rows=max_rows, filters=args)
    return {"rows": result}


@app.route("/tables/<table_name>", methods=["POST"])
def insert_to_table(table_name: str):
    data = request.json
    try:
        db_service.insert_into_table(table_name=table_name, row=data)
    except Exception as e:
        logger.exception(f"inserting the record into {table_name} failed")
        return {"error": str(e)}
    return {"status": "success"}


@app.route("/tables/<table_name>", methods=["PUT"])
def update_row(table_name: str):
    args = dict(request.args)
    body = request.json
    try:
        rows_count = db_service.update_row(table_name=table_name, filters=args, values_to_be_updated=body)
    except Exception as e:
        logger.exception(f"updating records failed")
        return {"error": str(e)}

    return {"affected rows": rows_count}


if __name__ == "__main__":
    app.run(port=9567)
