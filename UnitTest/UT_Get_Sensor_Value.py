from MOST.IPMIModule import IPMIManager
import time
import subprocess
import os
import socket
HOST = "compute2"
PORT = 2468
TYPE = ["02-CPU 1"]

def run():
	ipmi_manager = IPMIManager()
	result = ipmi_manager.getNodeInfoByType(TYPE)
	if result["code"] == 0:
		return True
	else:
		return False
