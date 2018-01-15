import sys

import Postprocess
import Preprocess

HOST = "compute3"
sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

sys.path.insert(0, '/home/' + HOST + '/Desktop/MOST/HASS/compute_node')


CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]


def run():
    cluster_id, instance_id = _create_cluster()

    delete_cluster(cluster_id)


def _create_cluster():
    ClusterManager.init()
    instance_id = Preprocess.create_with_provider_instance()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ClusterManager.addInstance(cluster_id, instance_id, write_DB=False, send_flag=False)
    return cluster_id, instance_id


def delete_cluster(cluster_id):
    ClusterManager.deleteNode(cluster_id, "compute1", write_DB=False)
    Postprocess.deleteInstance()

