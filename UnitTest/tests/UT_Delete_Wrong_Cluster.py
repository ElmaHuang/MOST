from MOST.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"

def run():
	ClusterManager.init()
	ClusterManager.createCluster(CLUSTER_NAME, write_DB = False)
	cluster_id = "wrong"
	try:
		result = ClusterManager.deleteCluster(cluster_id)
		if result["code"] == "1":
			return True
		else:
			return False
	except:
		return False