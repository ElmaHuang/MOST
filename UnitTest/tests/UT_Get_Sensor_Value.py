from MOST.IPMIModule import IPMIManager
import time
import subprocess
import os
import socket
HOST = "compute3"
TYPE = ["Inlet Temp"]

def run():
	ipmi_manager = IPMIManager()
	result = ipmi_manager.getNodeInfoByType(HOST,TYPE)
	if result["code"] == "0":
		return True
	else:
		return False
