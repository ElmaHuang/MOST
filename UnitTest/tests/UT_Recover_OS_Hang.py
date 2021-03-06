import socket
import sys
import time

import paramiko

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from IPMIModule import IPMIManager
from Node import Node

CLUSTER_ID = "clusterid"
HOST = "compute4"
PORT = 2468
ipmi_manager = IPMIManager()


def run():
    try:
        client = _create_ssh_client(HOST)
        cmd = "sudo sh /home/" + HOST + "/Desktop/MOST/HASS/compute_node/os_hang.sh"
        #cmd = "kill -SEGV 1 & ; kill -SEGV 1"
        #cmd = "sudo sh /home/compute4/Desktop/test.sh"
        stdin, stdout, stderr = _remote_exec(client, cmd)
        # print stdout.read()
        result = detection_OS_fail(20)
        if result:
            print "detect os successfuly"
            recover = recover_os_fail(180)
            if recover:
                return True
            else:
                return False
        else:
            print "detect os fail"
            return False
    except Exception as e:
        print str(e)


def recover_os_fail(detect_time=5):
    ipmi_manager.rebootNode(HOST)
    result = False
    try:
        while detect_time > 0:
            state = _get_detect_result()
            if "health" in state:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print str(e)
        result = False
    return result


def detection_OS_fail(detect_time=5):
    result = False
    try:
        while detect_time > 0:
            fail = _get_detect_result()
            print fail
            if "os" in fail:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print str(e)
        result = False
    return result


def _get_detect_result():
    node = Node(HOST, CLUSTER_ID)
    thread = node.detection_thread
    result = thread.detect()
    return result


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
    return stdin, stdout, stderr


def _create_ssh_client(name, default_timeout=1):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    try:
        client.connect(hostname=name, username='root', timeout=default_timeout)
        return client
    except Exception as e:
        print "Excpeption : %s" % str(e)
        return None


def _check_boot_up():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.settimeout(0.5)
    sock.connect((HOST, PORT))
    try:
        line = "polling request"
        sock.sendall(line)
        data, addr = sock.recvfrom(1024)
        return data
    except Exception as e:
        print str(e)
        return "Error"
