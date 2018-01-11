import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)["data"]["cluster_id"]
    try:
        result = ClusterManager.deleteCluster(cluster_id)
        if result.code == "succeed":
            return True
        else:
            return False
    except:
        return False
