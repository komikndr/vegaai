import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from sqlalchemy import create_engine


postgre_host = os.getenv("POSTGRE_DS_HOST")
postgre_port = os.getenv("POSTGRE_DS_PORT")
postgre_username = os.getenv("POSTGRE_DS_USERNAME")
postgre_password = os.getenv("POSTGRE_DS_PASSWORD")
postgre_schema = os.getenv("POSTGRE_DS_SCHEMA")


postgre_conn = f'postgresql://{postgre_username}:{postgre_password}@{postgre_host}:{postgre_port}/{postgre_schema}'
postgre_engine = create_engine(postgre_conn)
postgre_db = SQLDatabase(postgre_engine, include_tables=["rkpd", "commuter_schedule"])


def get_postgre_sql_toolkit(db=postgre_db, db_name="postgre"):
    return [InfoSQLDatabaseTool(db=db, name=f"{db_name}_sql_db_schema"),
            ListSQLDatabaseTool(db=db, name=f"{db_name}_sql_db_list_tables"),
            QuerySQLDataBaseTool(db=db, name=f"{db_name}_sql_db_query")]
