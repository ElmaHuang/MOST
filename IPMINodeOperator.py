#!/usr/bin/python
# -*- coding: utf-8 -*-

from NovaClient import NovaClient
from IPMIModule import IPMIManager
import time
from ClusterManager import ClusterManager
import ConfigParser
import logging
import socket


class Operator(object):
	def __init__(self):
		# self.clusterList =
		self.nova_client = NovaClient.getInstance()
		self.ipmi_module=IPMIManager()
		self.cluster_list=ClusterManager.getClusterList()
		config = ConfigParser.RawConfigParser()
		config.read('hass.conf')
		self.port = int(config.get("detection","polling_port"))


	def startNode(self,node_name, default_wait_time = 300):
		message = ""
		#code = ""
		result = None
		if self._checkNodeIPMI(node_name):
			#code = "0"
			message += " IPMIOperator--node is in compute pool . The node is %s." % node_name
			try:
				ipmi_result=self.ipmi_module.startNode(node_name)
				if ipmi_result["code"] == "0":
					boot_up = self._check_node_boot_success(node_name, default_wait_time)
					if boot_up:
						message += "start node success.The node is %s." % node_name
						logging.info(message)
						result = {"code": "0", "node_name": node_name, "message": message}
					else: raise Exception("check node boot fail")
				else :raise Exception("IpmiModule start node fail")
			except Exception as e:
			#start fail
				message += "IPMIOperator--start node fail.The node is %s.%s" % (node_name,e)
				logging.error(message)
				result = {"code": "1", "node_name": node_name, "message": message}
		else	:
			#code = "1"
			message += " IPMIOperator--node is not in compute pool or is not a IPMI PC . The node is %s." % node_name
			logging.error(message)
			result = {"code": "1", "node_name": node_name, "message": message}
		return result

	def shutOffNode(self,node_name):
		message = ""
		#result =None
		if self._checkNodeIPMI(node_name) and self._checkNodeNotInCluster(node_name):
			try:
				ipmi_result=self.ipmi_module.shutOffNode(node_name)
				#check power status in IPMIModule
				if ipmi_result["code"]== "0":
					message += "sthut off node success.The node is %s." % node_name
					logging.info(message)
					result = {"code": "0", "node_name": node_name, "message": message}
				else:raise Exception("IpmiModule shut off node fail")
			except Exception as e:
				# shut off fail
				message += "IPMIOperator--shut off node fail.The node is %s.%s" % (node_name, e)
				logging.error(message)
				result = {"code": "1", "node_name": node_name, "message": message}
		else:
			message += " IPMIOperator--node is not in compute pool or is not a IPMI PC or is already be protected. The node is %s." % node_name
			logging.error(message)
			result = {"code": "1", "node_name": node_name, "message": message}
		return result

	def rebootNode(self,node_name):
		message = ""
		if self._checkNodeIPMI(node_name) and  self._checkNodeNotInCluster(node_name):
			try:
				ipmi_result = self.ipmi_module.rebootNode(node_name)
				if ipmi_result["code"] == "0":
					message += "reboot node success.The node is %s." % node_name
					logging.info(message)
					result = {"code": "0", "node_name": node_name, "message": message}
				else:
					raise Exception("IpmiModule reboot node fail")
			except Exception as e:
				# shut off fail
				message += "IPMIOperator--reboot node fail.The node is %s.%s" % (node_name, e)
				logging.error(message)
				result = {"code": "1", "node_name": node_name, "message": message}
		else:
			message += " IPMIOperator--node is not in compute pool or is not a IPMI PC or is already be protected. The node is %s." % node_name
			logging.error(message)
			result = {"code": "1", "node_name": node_name, "message": message}
		return result

	def getAllInfoByNode(self,node_name):
		data = self.ipmi_module.getAllInfoByNode(node_name)
		return data

	def getNodeInfoByType(self,node_name,sensor_type):
		data=self.ipmi_module.getNodeInfoByType(node_name,sensor_type)
		return data

	def _checkNodeIPMI(self,node_name):
		#is IPMI PC
		ipmistatus = self.ipmi_module._getIPMIStatus(node_name)
		if not ipmistatus:
			return False
		#is in computing pool
		if node_name in self.nova_client.getComputePool():
			message = " node is in compute pool . The node is %s." % node_name
			logging.info(message)
			return True
		else:
			message = " node is not in compute pool please check again! The node is %s." % node_name
			logging.error(message)
			return False

	def _checkNodeNotInCluster(self,node_name):
		for cluster_id in self.cluster_list:
			cluster=ClusterManager.getCluster(cluster_id)
			node_list = cluster.getAllNodeStr()
			if node_name in node_list:
					return False
		return True

	def _check_node_boot_success(self, nodeName, check_timeout, timeout=1):
		#not be protect(not connect socket)
		#check power statue in IPMIModule
		#check detection agent
		status = False
		data = ""
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setblocking(0)
		sock.settimeout(1)
		while "OK" not in data and check_timeout > 0:
			try:
				sock.sendto("polling request", (nodeName, int(self.port)))
				data, addr = sock.recvfrom(2048)
			except Exception as e:
				print e
			if "OK" in data:
				status = True
				sock.close()
			else:
				time.sleep(1)
				check_timeout -= 1
		return status