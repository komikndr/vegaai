import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from sqlalchemy import create_engine
import pyhive

hive_host = os.getenv("HIVE_HOST")
hive_port = os.getenv("HIVE_PORT")
hive_username = os.getenv("HIVE_USERNAME")
hive_schema = os.getenv("HIVE_SCHEMA")

hive_conn = f'hive://{hive_username}@{hive_host}:{hive_port}/{hive_schema}'
hive_engine = create_engine(hive_conn)

hive_db = SQLDatabase(hive_engine)


def get_hive_sql_toolkit(db=hive_db, db_name="hive"):
    return [InfoSQLDatabaseTool(db=db, name=f"{db_name}_sql_db_schema"),
            ListSQLDatabaseTool(db=db, name=f"{db_name}_sql_db_list_tables"),
            QuerySQLDataBaseTool(db=db, name=f"{db_name}_sql_db_query")]
