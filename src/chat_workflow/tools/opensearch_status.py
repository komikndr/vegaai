import httpx
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel
from typing import List, Dict, Optional
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
import chainlit as cl


class OpenSearchClusterHealth(BaseModel):
    cluster_name: str
    status: str
    timed_out: bool
    number_of_nodes: int
    number_of_data_nodes: int
    discovered_master: bool
    discovered_cluster_manager: bool
    active_primary_shards: int
    active_shards: int
    relocating_shards: int
    initializing_shards: int
    unassigned_shards: int
    delayed_unassigned_shards: int
    number_of_pending_tasks: int
    number_of_in_flight_fetch: int
    task_max_waiting_in_queue_millis: int
    active_shards_percent_as_number: float


class IOUsageStats(BaseModel):
    max_io_utilization_percent: str


class ResourceUsageStats(BaseModel):
    cpu_utilization_percent: str
    memory_utilization_percent: str
    io_usage_stats: IOUsageStats


class NodeAttributes(BaseModel):
    rack: Optional[str]
    shard_indexing_pressure_enabled: Optional[str]


class NodeInfo(BaseModel):
    name: str
    host: str
    ip: str
    roles: List[str]
    attributes: NodeAttributes
    resource_usage_stats: Dict[str, ResourceUsageStats]


class NodeStatsResponse(BaseModel):
    nodes: Dict[str, NodeInfo]


async def get_opensearch_cluster_health():
    url = "https://10.10.5.11:9220/_cluster/health"
    auth = ("admin", "admin")  # Replace with OpenSearch username and password

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(url, auth=auth)
            response.raise_for_status()

            # Parse and return the validated response as a dictionary
            cluster_health = OpenSearchClusterHealth.parse_obj(response.json())
            return cluster_health.dict()

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except ValueError as e:
            print(f"Error parsing response: {e}")


@tool
async def get_opensearch_general_health():
    """
    Fetches node information regarding General OpenSearch/ElasticSearch

    Args:
        None

    Returns:
        None
    """
    opensearch_props = await get_opensearch_cluster_health()
    opensearch_element = cl.CustomElement(name="SearchClusterHealth", props=opensearch_props)
    await cl.Message(content="Here is the ticket information!", elements=[opensearch_element]).send()
    return opensearch_props

@tool
async def get_opensearch_node_info(state) -> Dict:
    """
    Fetches node information regarding OpenSearch/ElasticSearch
    including host, IP, roles, and resource usage stats

    Args:
        None

    Returns:
        Dict: A dictionary containing the extracted information.
    """
    api_url = (
            "http://localhost:9200/_nodes/stats/resource_usage_stats"
    )
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(api_url, auth=("admin", "admin"))
            response.raise_for_status()
            data = response.json()

            # Parse using Pydantic
            parsed_data = NodeStatsResponse(**data)

            # Extract information
            results = []
            for node_id, node_info in parsed_data.nodes.items():
                resource_usage = node_info.resource_usage_stats.get(node_id, {})
                results.append(
                    {
                        "host": node_info.host,
                        "ip": node_info.ip,
                        "roles": node_info.roles,
                        "cpu_utilization_percent": resource_usage.cpu_utilization_percent,
                        "memory_utilization_percent": resource_usage.memory_utilization_percent,
                        "max_io_utilization_percent": resource_usage.io_usage_stats.max_io_utilization_percent,
                    }
                )
            return {"nodes": results}

        except Exception as e:
            return {"error": str(e)}

