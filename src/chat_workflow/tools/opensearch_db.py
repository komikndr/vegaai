from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from sqlalchemy import create_engine

import es

ssl_args = {"use_ssl": True, "verify_certs": False, "ssl_show_warn": False}
opensearch_engine = create_engine("odelasticsearch+https://admin:admin@locahost:9200/", connect_args=ssl_args)
opensearch_db = SQLDatabase(opensearch_engine)


def get_opensearch_sql_toolkit(db=opensearch_db, db_name="elastic"):
    return [InfoSQLDatabaseTool(db=db, name=f"{db_name}_sql_db_schema"),
            ListSQLDatabaseTool(db=db, name=f"{db_name}_sql_db_list_tables"),
            QuerySQLDataBaseTool(db=db, name=f"{db_name}_sql_db_query")]
