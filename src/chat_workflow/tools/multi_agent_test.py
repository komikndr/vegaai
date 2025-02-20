from langchain_core.tools import tool

@tool
def get_weather(city: str):
    """check the weather of city"""
    return f"{city} is sunny"


@tool
def get_humidty(city: str):
    """Check humidty of the city"""
    return f"{city} is very humid"


@tool
def get_vacation_place():
    """Check nice location to hangout"""
    return "Mc Donald is nice place to hangout"


@tool
def call_model(state):
    """This is just bypass for internal system purpose, dont mind this"""
    return ""

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from sqlalchemy import create_engine


sys_engine = create_engine("sqlite:////home/kxn/research-onyx-ai/abel/db/eve_sys.sqlite")
dim_engine = create_engine("sqlite:////home/kxn/research-onyx-ai/abel/db/dim_system.sqlite")
db_sys = SQLDatabase(sys_engine)
db_dim = SQLDatabase(dim_engine)

def get_sql_toolkit():
    db = SQLDatabase(engine)
    return [InfoSQLDatabaseTool(db=db),
            ListSQLDatabaseTool(db=db),
            QuerySQLDataBaseTool(db=db)]
