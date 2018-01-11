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


def run(check_timeout=300):
    node = Node(HOST, CLUSTER_ID)
    thread = node.detection_thread
    client = _create_ssh_client(HOST)
    ipmi_manager = IPMIManager()
    _remote_exec(client, "sudo poweroff -f")
    print "wait %s to shutoff" % HOST
    time.sleep(15)
    result = False
    try:
        detect_time = 5
        while detect_time > 0:
            fail = thread.detect()
            print fail
            if fail == "power":
                result = True
            detect_time -= 1
            time.sleep(1)
        result = False
    except Exception as e:
        print str(e)
        result = False
    finally:
        ipmi_manager.startNode(HOST)
        return result
        '''
        boot_up = None
        while check_timeout > 0:
            boot_up = _check_boot_up()
            if boot_up == "OK":
                print "%s boot up!" % HOST
                check_timeout = 0
            time.sleep(1)
            check_timeout -= 1
        if boot_up != "OK":
            print "%s not boot up!" % HOST
            return False
        '''


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdin, stdout, stderr


def _create_ssh_client(name, default_timeout=1):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(name, username='root', timeout=default_timeout)
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
