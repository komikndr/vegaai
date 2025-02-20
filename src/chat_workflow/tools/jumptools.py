import pandas as pd
import sqlite3
import requests

from typing import List

from langchain_core.tools import tool

# EVE_SYS_DB_PATH = "../../../db/eve_sys.sqlite"
EVE_SYS_DB_PATH = "/home/kxn/research-onyx-ai/abel/db/eve_sys.sqlite"


def query_sqlite(query, db_path, params=None):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn, params)


@tool
async def jump_navigator(
    start_system_name: str, end_system_name: str, security_flag: str
) -> List[str]:
    """
    Fetch the route from start_system_name to end_system_name using the EVE Online API.
    Converts the returned list of system IDs into system names using the SQLite database.

    Parameters:
        - start_system_name (str): Origin system name.
        - end_system_name (str): Destination system name.
        - security_flag (str): One of 'shortest', 'secure', or 'insecure'.

    Returns:
        - List[str]: Solar system names along the route.
    """
    # Fetch system IDs from names
    solar_system_names = [start_system_name, end_system_name]
    case_statement = (
        "CASE solarSystemName\n"
        + "\n".join(
            f"WHEN '{name}' THEN {i+1}" for i, name in enumerate(solar_system_names)
        )
        + "\nEND"
    )

    query = f"""
    SELECT solarSystemID
    FROM mapSolarSystems
    WHERE solarSystemName IN ({','.join(f"'{name}'" for name in solar_system_names)})
    ORDER BY {case_statement};
    """

    result = query_sqlite(query, EVE_SYS_DB_PATH)
    if result.empty or len(result) < 2:
        raise ValueError("Could not retrieve both start and end system IDs.")
    start_system_id, end_system_id = result["solarSystemID"].tolist()

    # Fetch route from the EVE Online API
    url = f"https://esi.evetech.net/v1/route/{start_system_id}/{end_system_id}/"
    params = {"flag": security_flag}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ValueError(
            f"API call failed with status code {response.status_code}: {response.text}"
        )

    system_ids = response.json()

    # Fetch system names based on IDs
    case_statement = (
        "CASE solarSystemID\n"
        + "\n".join(f"WHEN {id} THEN {i+1}" for i, id in enumerate(system_ids))
        + "\nEND"
    )

    query = f"""
    SELECT solarSystemName
    FROM mapSolarSystems
    WHERE solarSystemID IN ({','.join(map(str, system_ids))})
    ORDER BY {case_statement};
    """

    result = query_sqlite(query, EVE_SYS_DB_PATH)
    if result.empty:
        raise ValueError("Could not retrieve system names for the route.")

    return result["solarSystemName"].tolist()

