from MOST.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
def run():
	try:
		ClusterManager.init()
		result = ClusterManager.createCluster(CLUSTER_NAME, write_DB = False)
		if result["code"] == "0":
			return True
		else:
			return False
	except:
		return False