#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains recovery methods.
##########################################################


import ConfigParser
import logging
import subprocess
import time

import State
from ClusterManager import ClusterManager
from DatabaseManager import IIIDatabaseManager
from Detector import Detector
from NovaClient import NovaClient


class RecoveryManager(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.recover_function = {State.NETWORK_FAIL: self.recoverNetworkIsolation,
                                 State.SERVICE_FAIL: self.recoverServiceFail,
                                 State.POWER_FAIL: self.recoverPowerOff,
                                 State.SENSOR_FAIL: self.recoverSensorCritical,
                                 State.OS_FAIL: self.recoverOSHanged}
        self.iii_support = self.config.getboolean("iii", "iii_support")
        self.iii_database = None

    def recover(self, fail_type, cluster_id, fail_node_name):
        return self.recover_function[fail_type](cluster_id, fail_node_name)

    def recoverOSHanged(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print "fail node is %s" % fail_node.name
        print "start recovery vm"
        self.recoverVM(cluster, fail_node)
        print "end recovery vm"
        return self.recoverNodeByReboot(fail_node)

    def recoverPowerOff(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print "fail node is %s" % fail_node.name
        print "start recovery vm"
        self.recoverVM(cluster, fail_node)
        print "end recovery vm"
        return self.recoverNodeByStart(fail_node)

    def recoverNodeCrash(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print "fail node is %s" % fail_node.name
        print "start recovery vm"
        self.recoverVM(cluster, fail_node)
        print "end recovery vm"
        return self.recoverNodeByShutoff(fail_node)

    def recoverNetworkIsolation(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)

        network_transient_time = int(self.config.get("default", "network_transient_time"))
        second_chance = State.HEALTH
        try:
            print "start second_chance..."
            print "wait %s seconds and check again" % network_transient_time
            time.sleep(network_transient_time)  # sleep certain transient seconds and ping host again
            response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', fail_node.name],
                                               stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError:
            print "After 30 senconds, the network status of %s is still unreachable" % fail_node.name
            second_chance = State.NETWORK_FAIL

        if second_chance == State.HEALTH:
            print "The network status of %s return to health" % fail_node.name
            return True
        else:
            print "fail node is %s" % fail_node.name
            print "start recovery vm"
            self.recoverVM(cluster, fail_node)
            print "end recovery vm"
            return self.recoverNodeByReboot(fail_node)

    def recoverSensorCritical(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print "fail node is %s" % fail_node.name
        print "start recovery vm"
        self.recoverVM(cluster, fail_node)
        print "end recovery vm"
        return self.recoverNodeByShutoff(fail_node)

    def recoverServiceFail(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)

        port = int(self.config.get("detection", "polling_port"))
        version = int(self.config.get("version", "version"))
        detector = Detector(fail_node, port)
        fail_services = detector.getFailServices()

        status = True
        if "agents" in fail_services:
            status = self.restartDetectionService(fail_node, version)
        else:
            status = self.restartServices(fail_node, fail_services, version)

        if not status:  # restart service fail
            print "start recovery"
            print "fail node is %s" % fail_node.name
            print "start recovery vm"
            self.recoverVM(cluster, fail_node)
            print "end recovery vm"
            return self.recoverNodeByReboot(fail_node)
        else:
            return status  # restart service success

    def recoverVM(self, cluster, fail_node):
        if len(cluster.getNodeList()) < 2:
            logging.error("RecoverManager : evacuate fail, cluster only one node")
            return
        if not fail_node:
            logging.error("RecoverManager : not found the fail node")
            return
        target_host = cluster.findTargetHost(fail_node)
        print "target_host : %s" % target_host.name
        if not target_host:
            logging.error("RecoverManager : not found the target_host %s" % target_host)

        protected_instance_list = cluster.getProtectedInstanceListByNode(fail_node)
        print "protected list : %s" % protected_instance_list
        for instance in protected_instance_list:
            if target_host.instanceOverlappingInLibvirt(instance):
                print "instance %s overlapping in %s" % (instance.name, target_host.name)
                print "start undefine instance in %s" % target_host.name
                target_host.undefineInstance(instance)
                print "end undefine instance"

            try:
                print "start evacuate"
                cluster.evacuate(instance, target_host, fail_node)
            except Exception as e:
                print str(e)
                logging.error("RecoverManager - The instance %s evacuate failed" % instance.id)

        print "check instance status"
        status = self.checkInstanceNetworkStatus(fail_node, cluster)
        if status == False:
            logging.error("RecoverManager : check vm network status false")
        print "update instance"
        cluster.updateInstance()

        if self.iii_support:
            self.iii_database = IIIDatabaseManager()
            print "start modify iii database"
            for instance in protected_instance_list:
                try:
                    self.iii_database.updateInstance(instance.id, target_host.name)
                except Exception as e:
                    print str(e)
                    logging.error("%s" % str(e))
            print "end modify iii database"

    def recoverNodeByReboot(self, fail_node):
        print "start recover node by reboot"
        result = fail_node.reboot()
        print "boot node result : %s" % result.message
        message = "RecoveryManager recover network isolation"
        if result.code == "succeed":
            logging.info(message + result.message)
            boot_up = self.checkNodeBootSuccess(fail_node)
            if boot_up:
                print "Node %s recovery finished." % fail_node.name
                return True
            else:
                logging.error(message + "Can not reboot node %s successfully", fail_node.name)
                return False
        else:
            logging.error(message + result.message)
            return False

    def recoverNodeByShutoff(self, fail_node):
        print "start recover node by shutoff"
        result = fail_node.shutoff()
        if result.code == "succeed":
            return False  # shutoff need to remove from cluster, so return False
        else:
            logging.error(result.message)
            print result.message

    def recoverNodeByStart(self, fail_node):
        print "start recover node by start"
        result = fail_node.start()
        print "boot node result : %s" % result.message
        message = "RecoveryManager recover network isolation"
        if result.code == "succeed":
            logging.info(message + result.message)
            boot_up = self.checkNodeBootSuccess(fail_node)
            if boot_up:
                print "Node %s recovery finished." % fail_node.name
                return True
            else:
                logging.error(message + "Can not start node %s successfully", fail_node.name)
                return False
        else:
            logging.error(message + result.message)
            return False

    def restartDetectionService(self, fail_node, version):
        print "Start service failure recovery by starting Detection Agent"
        agent_path = self.config.get("path", "agent_path")
        cmd = "cd /home/%s/%s/ ; python DetectionAgent.py" % (fail_node.name, agent_path)  # not daemon
        print cmd
        # if version = 16:
        # 	cmd = "systemctl restart DetectionAgent.py" # 16 daemon
        # elif version = 14:
        # 	cmd = "service DetectionAgent.py restart" # 14 daemon
        try:
            fail_node.remote_exec(cmd)  # restart DetectionAgent service
            time.sleep(5)

            cmd = "ps aux | grep '[D]etectionAgent.py'"
            stdin, stdout, stderr = fail_node.remote_exec(cmd)
            service = stdout.read()
            print service
            if "python DetectionAgent.py" in service:  # check DetectionAgent
                return True
            return False
        except Exception as e:
            print str(e)
            return False

    def restartServices(self, fail_node, fail_services, version, check_timeout=60):
        service_mapping = {"libvirt": "libvirt-bin", "nova": "nova-compute", "qemukvm": "qemu-kvm"}
        fail_service_list = fail_services.split(":")[-1].split(";")[0:-1]

        try:
            for fail_service in fail_service_list:
                fail_service = service_mapping[fail_service]
                if version == 16:
                    cmd = "systemctl restart %s" % fail_service
                else:
                    cmd = "sudo service %s restart" % fail_service
                print cmd
                stdin, stdout, stderr = fail_node.remote_exec(cmd)  # restart service

                while check_timeout > 0:
                    if version == 14:
                        cmd = "service %s status" % fail_service
                    elif version == 16:
                        cmd = "systemctl status %s | grep active" % fail_service
                    stdin, stdout, stderr = fail_node.remote_exec(cmd)  # check service active or not

                    if not stdout.read():
                        print "The node %s service %s still doesn't work" % (fail_node.name, fail_service)
                    else:
                        print "The node %s service %s successfully restart" % (fail_node.name, fail_service)
                        return True  # recover all the fail service
                    time.sleep(1)
                    check_timeout -= 1
                return False
        except Exception as e:
            print str(e)
            return False

    def checkInstanceNetworkStatus(self, fail_node, cluster, check_timeout=60):
        status = False
        fail = False
        protected_instance_list = cluster.getProtectedInstanceListByNode(fail_node)
        for instance in protected_instance_list:
            openstack_instance = self.nova_client.getVM(instance.id)
            try:
                if "provider" in openstack_instance.networks:
                    ip = str(openstack_instance.networks['provider'][0])
                else:
                    ip = str(openstack_instance.networks['selfservice'][1])
                status = self._pingInstance(ip, check_timeout)
            except Exception as e:
                print "vm : %s has no floating network, abort ping process!" + str(e) % instance.name
                continue
            if not status:
                fail = True
                logging.error("vm %s cannot ping %s" % (instance.name, ip))
        return fail

    def _pingInstance(self, ip, check_timeout):
        status = False
        time.sleep(5)
        while check_timeout > 0:
            try:
                print "check vm %s" % ip
                response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                                   universal_newlines=True)
                status = True
                break
            except subprocess.CalledProcessError:
                status = False
            finally:
                time.sleep(1)
                check_timeout -= 1
        return status

    def checkNodeBootSuccess(self, node, check_timeout=300):
        port = int(self.config.get("detection", "polling_port"))
        detector = Detector(node, port)
        print "waiting node to reboot"
        time.sleep(5)
        print "start check node booting"
        while check_timeout > 0:
            try:
                if detector.checkServiceStatus() == State.HEALTH:
                    return True
            except Exception as e:
                print str(e)
            finally:
                time.sleep(1)
                check_timeout -= 1
        return False


if __name__ == "__main__":
    r = RecoveryManager()
    # l = r.remote_exec("compute3","virsh list --all")
