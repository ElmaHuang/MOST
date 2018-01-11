import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")

    try:
        ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
        result = ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
        if result.code == "succeed":
            return False
        else:
            return True
    except:
        return True
    finally:
        ClusterManager.deleteNode(cluster_id, "compute1", write_DB=False)
