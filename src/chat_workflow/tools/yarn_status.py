import httpx
from typing import List, Optional, Union
from pydantic import BaseModel, parse_obj_as
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from langchain_core.tools import tool

# General Cluster info (This is for description stuff)
YARN_GENERAL_URL = "http://localhost:8088/ws/v1/cluster/"

# General Cluster Metric (This is for general metrics)
YARN_CLUSTER_METRICS = "http://localhost:8088/ws/v1/cluster/metrics"

# YARN app statsm, where application type can be
# - spark
# - mapreduce
# - tez
#
# YARN_APP_STATS = "http://localhost:8088/ws/v1/cluster/appstatistics?&applicationTypes=spark"
YARN_APP_STATS = "http://localhost:8088/ws/v1/cluster/appstatistics"

# Node Metrics
# http://localhost:8088/ws/v1/cluster/nodes


######### FOR def get_yarn_cluster_info #########
class ClusterInfo(BaseModel):
    id: int
    startedOn: datetime
    state: str
    haState: str
    rmStateStoreName: str
    resourceManagerVersion: str
    resourceManagerBuildVersion: str
    resourceManagerVersionBuiltOn: datetime
    hadoopVersion: str
    hadoopBuildVersion: str
    hadoopVersionBuiltOn: datetime
    haZooKeeperConnectionState: str

    @staticmethod
    def parse_timestamp(timestamp):
        utc_plus7 = ZoneInfo("Asia/Jakarta")
        try:
            # Handle millisecond timestamps
            dt = datetime.fromtimestamp(int(timestamp) / 1000, timezone.utc)
        except ValueError:
            # Fallback for ISO 8601 formatted strings
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.astimezone(utc_plus7)

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            id=data["id"],
            startedOn=cls.parse_timestamp(data["startedOn"]),
            state=data["state"],
            haState=data["haState"],
            rmStateStoreName=data["rmStateStoreName"],
            resourceManagerVersion=data["resourceManagerVersion"],
            resourceManagerBuildVersion=data["resourceManagerBuildVersion"],
            resourceManagerVersionBuiltOn=cls.parse_timestamp(
                data["resourceManagerVersionBuiltOn"]
            ),
            hadoopVersion=data["hadoopVersion"],
            hadoopBuildVersion=data["hadoopBuildVersion"],
            hadoopVersionBuiltOn=cls.parse_timestamp(data["hadoopVersionBuiltOn"]),
            haZooKeeperConnectionState=data["haZooKeeperConnectionState"],
        )


######### FOR def get_yarn_cluster_metrics #########
class ResourceInformation(BaseModel):
    name: str
    units: Optional[str]
    value: int


class ResourceInformations(BaseModel):
    resourceInformation: List[ResourceInformation]


class Resources(BaseModel):
    memory: int
    vCores: int
    # resourceInformations: ResourceInformations


class ClusterMetrics(BaseModel):
    appsSubmitted: int
    appsCompleted: int
    appsPending: int
    appsRunning: int
    appsFailed: int
    appsKilled: int
    reservedMB: int
    availableMB: int
    allocatedMB: int
    reservedVirtualCores: int
    availableVirtualCores: int
    allocatedVirtualCores: int
    containersAllocated: int
    containersReserved: int
    containersPending: int
    totalMB: int
    totalVirtualCores: int
    totalNodes: int
    lostNodes: int
    unhealthyNodes: int
    decommissioningNodes: int
    decommissionedNodes: int
    rebootedNodes: int
    activeNodes: int
    shutdownNodes: int


class ClusterViewResponse(BaseModel):
    clusterMetrics: Optional[ClusterMetrics]
    totalUsedResourcesAcrossPartition: Optional[Resources]
    totalClusterResourcesAcrossPartition: Optional[Resources]


######### FOR def get_yarn_app_stats #########
class StatItem(BaseModel):
    state: str
    type: str
    count: int


class AppStatInfo(BaseModel):
    statItem: List[StatItem]


@tool
async def get_yarn_cluster_info():
    """
    Fetches and parses information about the YARN cluster from a predefined URL.

    This tool retrieves cluster metadata from the YARN ResourceManager's REST API,
    parses the response into a structured Python object, and returns detailed
    information about the cluster's state, version, and runtime.

    The data includes:
    - Cluster ID and start time
    - ResourceManager state and high-availability (HA) state
    - ResourceManager and Hadoop versions and build details
    - ZooKeeper connection state for high availability

    Returns:
        - If successful: A `ClusterInfo` object containing all parsed cluster details.
        - If unsuccessful: A string with the HTTP error code (e.g., "Error: 404").
    """
    url = YARN_GENERAL_URL
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            cluster_info = ClusterInfo.from_json(data["clusterInfo"])
            return cluster_info
        else:
            return f"Error: {response.status_code}"


@tool
async def get_yarn_cluster_metrics(view_type: str) -> Union[BaseModel, str]:
    """
    Fetches specific cluster information from the YARN cluster metrics API based on the provided view_type.

    Args:
    - view_type: One of "general", "resourceUsed", or "resourceAvailable" to select the specific part of the data.

    Returns:
    - Parsed Pydantic model instance or string with the relevant data based on the view_type.
    """
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.get(YARN_CLUSTER_METRICS, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if view_type == "general":
                cluster_metrics = parse_obj_as(
                    ClusterMetrics, data.get("clusterMetrics", {})
                )
                return cluster_metrics

            elif view_type == "resourceUsed":
                total_used_resources = parse_obj_as(
                    Resources,
                    data.get("clusterMetrics", {}).get(
                        "totalUsedResourcesAcrossPartition", {}
                    ),
                )
                return total_used_resources

            elif view_type == "resourceAvailable":
                total_cluster_resources = parse_obj_as(
                    Resources,
                    data.get("clusterMetrics", {}).get(
                        "totalClusterResourcesAcrossPartition", {}
                    ),
                )
                return total_cluster_resources
            else:
                return "Invalid view type. Please provide 'info', 'resourceUsed', or 'resourceAvailable'."
        else:
            return f"Error: {response.status_code}"


@tool
async def get_yarn_app_stats(app_type: str) -> Union[AppStatInfo, str]:
    """
    Fetches the application statistics for a specific YARN application type.

    Args:
        app_type (str): The type of YARN application. It must be one of `spark`, `tez`, or `mapreduce`.

    Returns:
        Union[AppStatInfo, str]: Returns an instance of `AppStatInfo` if the request is successful.
                                If an invalid `app_type` is passed, returns an error message.
    """
    headers = {"Accept": "application/json"}

    if app_type not in ["spark", "tez", "mapreduce"]:
        return f"{app_type} is not a valid parameter, use either `spark`, `tez`, or `mapreduce`"

    url = f"{YARN_APP_STATS}?&applicationTypes={app_type}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return AppStatInfo.parse_obj(
                data["appStatInfo"]
            )
        else:
            return f"Error: {response.status_code}"
