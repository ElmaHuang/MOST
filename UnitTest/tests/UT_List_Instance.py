import sys
import Preprocess
import Postprocess

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager


CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]


def run():
    ClusterManager.init()
    instance_id = Preprocess.create_with_provider_instance()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ClusterManager.addInstance(cluster_id, instance_id, write_DB=False, send_flag=False)

    try:
        result = ClusterManager.listInstance(cluster_id, send_flag=False)
        instance_list = result.data.get("instance_list")
        if len(instance_list) == 1:
            return True
        else:
            return False
    except:
        return False
    finally:
        ClusterManager.deleteNode(cluster_id, "compute1", write_DB=False)
        Postprocess.deleteInstance()
