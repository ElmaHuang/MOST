from MOST.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]

def run():
	ClusterManager.init()
	cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB = False)["clusterId"]
	ClusterManager.addNode(cluster_id, NODE_NAME, write_DB = False)
	try:
		result = ClusterManager.deleteNode(cluster_id, NODE_NAME[0], write_DB = False)
		if result["code"] == "0":
			return True
		else:
			return False
	except:
		return False