import sys
sys.path.insert(0,'/home/controller/Desktop/MOST/HASS')
from DetectionThread import DetectionThread
from IPMIModule import IPMIManager
from Node import Node
import Preprocess
import Postprocess
import Config
import paramiko
import socket
import time


CLUSTER_ID = "clusterid"
HOST = "compute3"
PORT = 2468

def run(check_timeout = 300):
	node = Node(HOST,CLUSTER_ID)
	thread = node.detection_thread
	client = _create_ssh_client(HOST)
	ipmi_manager = IPMIManager()

	_remote_exec(client, "sudo kill -segv 1 && sudo kill -segv 1")
	detect_time = 5
	try:
		while detect_time > 0:
			fail = thread.detect()
			print fail
			if fail == "os":
				return True
			detect_time -= 1
			time.sleep(1)
		return False
	except Exception as e:
		print str(e)
	finally:
		ipmi_manager.rebootNode(HOST)
		time.sleep(5) # wait node to reboot
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

def _remote_exec(client, cmd):
	stdin, stdout, stderr = client.exec_command(cmd)
	return stdin, stdout, stderr

def _create_ssh_client(name,default_timeout=1):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		client.connect(name, username='root', timeout = default_timeout)
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