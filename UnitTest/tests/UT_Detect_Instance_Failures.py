import subprocess
import sys
import time

import Postprocess
import Preprocess

HOST = "compute3"
sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

sys.path.insert(0, '/home/' + HOST + '/Desktop/MOST/HASS/compute_node')
from InstanceFailures import InstanceFailures

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]


def run():
    try:
        cluster_id, instance_id = _create_cluster()
        instance_name = Preprocess._get_instance_name(instance_id)
        pid = _local_get_output("ps aux | grep " + instance_name + " | awk '{ print $2 }'")
        print "pid:",pid
        _local_exec("sudo kill -9 %s" % pid)
        detection = detect_instance_failure(20)
        if detection:
            return True
        else:
            return False

    except Exception as e:
        print str(e)
        return False
    finally:
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


def _local_exec(cmd):
    p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, shell=False, stdout=open(os.devnull, 'w'))
    return p.communicate()


def _local_get_output(cmd):
    result = subprocess.check_output(cmd, shell=True)
    # print str(result)
    return result


def detect_instance_failure(timeout=5):
    result = False
    try:
        while timeout > 0:
            if InstanceFailures.failed_instance != []:
                return True
            else:
                timeout -= 1
                time.sleep(1)
    except Exception as e:
        print str(e)
        result = False
    finally:
        return result
