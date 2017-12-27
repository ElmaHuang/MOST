from MOST.ClusterManager import ClusterManager
import Preprocess
import Postprocess

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]

def run():
	ClusterManager.init()
	instance_id = Preprocess.create_with_provider_instance()
	cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB = False)["clusterId"]
	ClusterManager.addNode(cluster_id, NODE_NAME, write_DB = False)
	ClusterManager.addInstance(cluster_id, instance_id, write_DB=False)
	
	wrong_cluster_id = "wrong id"
	try:
		result = ClusterManager.listInstance(wrong_cluster_id)
		if result["code"] == 0:
			return False
	except:
		return True
	finally:
		ClusterManager.deleteNode(cluster_id, "compute1", write_DB=False)
		Postprocess.deleteInstance()