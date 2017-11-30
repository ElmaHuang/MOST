from ClusterInterface import ClusterInterface
#from DetectionManager import DetectionManager
from Node import Node
from Instance import Instance
import socket
import uuid
import logging
import ConfigParser

class Cluster(ClusterInterface):
	def __init__(self, id , name):
		super(Cluster, self).__init__(id, name)

	def addNode(self, node_name_list):
		# create node list
		message =""
		if node_name_list == []: raise Exception
		try:
			for node_name in node_name_list:
				if  self._isInComputePool(node_name) :
					#print node_name_list
					node = Node(name = node_name , cluster_id = self.id)
					self.node_list.append(node)
					node.startDetectionThread()
					message = "Cluster--The node %s is added to cluster." % self.getAllNodeStr()
					logging.info(message)
					result = {"code": "0","clusterId": self.id,"node":node_name, "message": message}
				else:
					message += "the node %s is illegal.  " %node_name
					logging.error(message)
		except Exception as e:
			message = "Cluster-- add node fail , some node maybe overlapping or not in compute pool please check again! The node list is %s." % (self.getAllNodeStr())
			logging.error(message)
			result = {"code": "1", "clusterId": self.id, "message": message}
		finally:
			return result

	def deleteNode(self , node_name):
		try:
			node = self.getNodeByName(node_name)
			#stop Thread
			node.deleteDetectionThread()
			self.deleteInstanceByNode(node)
			self.node_list.remove(node)
			#ret = self.getAllNodeInfo()
			for node in self.node_list:
				if node.name == node_name:raise Exception
			message = "Cluster delete node success! node is %s , node list is %s,cluster id is %s." % (node_name, self.getAllNodeStr(),self.id)
			logging.info(message)
			result = {"code": "0","clusterId": self.id, "node":node_name, "message": message}
		except Exception as e:
			print str(e)
			message = "Cluster delete node fail , node maybe not in compute pool please check again! node is %s  The node list is %s." % (node_name,self.getAllNodeStr())
			logging.error(message)
			result = {"code": "1", "node":node_name,"clusterId": self.id, "message": message}
		finally:
			return result

	def getAllNodeInfo(self):
		ret = []
		for node in self.node_list:
			ret.append(node.getInfo())
		return ret

	def addInstance(self , instance_id):
		#self.host = None
		'''
		if self.isProtected(instance_id): # check instance is already being protected
			raise Exception("this instance is already being protected!")
		'''
		if  not self.checkInstanceExist(instance_id):
				raise Exception("Not any node have this instance!")
		elif not self.checkInstanceGetVolume(instance_id):
				raise Exception("Instance don't have Volume")
		elif not self.checkInstancePowerOn(instance_id):
			raise Exception("this instance is power off!")
		else:
			try:
				#Live migration VM to cluster node
				#print "start live migration"
				final_host = self.checkInstanceHost(instance_id)
				if final_host == None:
					final_host=self.liveMigrateInstance(instance_id)
				instance = Instance(id=instance_id,name=self.nova_client.getInstanceName(instance_id),host=final_host)
				self.sendUpdateInstance(final_host)
				self.instance_list.append(instance)
				message = "Cluster--Cluster add instance success ! The instance id is %s." % (instance_id)
				logging.info(message)
				result = {"code":"0","cluster id":self.id,"node":final_host,"instance id":instance_id,"message":message}
			except Exception as e:
				print str(e)
				message = "Cluster--Cluster add instance fail ,please check again! The instance id is %s." % (instance_id)
				logging.error(message)
				result = {"code":"1","cluster id":self.id,"instance id":instance_id,"message":message}
			finally:
				return result

	def deleteInstance(self , instance_id):
		if not self.isProtected(instance_id):
			raise Exception("this instance is not being protected")
		for instance in self.instance_list:
			host = instance.host
			if instance.id == instance_id:
				self.instance_list.remove(instance)
				self.sendUpdateInstance(host)
		#if instanceid not in self.instacne_list:
		message = "Cluster--delete instance success. this instance is now deleted (instance_id = %s)" % instance_id
		logging.info(message)
		result = {"code": "0", "clusterId": self.id, "instance id": instance_id, "message": message}
		return result

	def deleteInstanceByNode(self, node):
		protected_instance_list = self.getProtectedInstanceListByNode(node)
		for instance in protected_instance_list:
			self.deleteInstance(instance.id)
	#list Instance
	def getAllInstanceInfo(self,send_flag):
		ret = []
		#instance_list = self.getProtectedInstanceList()
		for instance in self.instance_list[:]:
			info = instance.getInfo()
			#for status in info[]:
			if "SHUTOFF" in info:
				self.deleteInstance(info[0])
			elif info[2] not in self.getAllNodeStr():
				self.deleteInstance(info[0])
			else :
				ret.append(info)
			if send_flag == True:self.sendUpdateInstance(instance.host)
		return ret
	#cluster.addInstance
	def findNodeByInstance(self, instance_id):
		for node in self.node_list:
			if node.containsInstance(instance_id):
				return node
		return None

	'''
	def _isNodeDuplicate(self , unchecked_node_name):
		for node in self.node_list:
			if node.name == unchecked_node_name:
				return True
		return False
		
	#addNode call
	def _getIPMIStatus(self, node_name):
		config = ConfigParser.RawConfigParser()
		config.read('hass.conf')
		ip_dict = dict(config._sections['ipmi'])
		return node_name in ip_dict
		
	def _nodeIsIllegal(self , unchecked_node_name):
		if not self._isInComputePool(unchecked_node_name):
			return True
		#if self._isNodeDuplicate(unchecked_node_name):
			#return True
		return False		
	'''

	def _isInComputePool(self, unchecked_node_name):
		return unchecked_node_name in self.nova_client.getComputePool()

	#be DB called
	def getNodeList(self):
		return self.node_list

	def sendUpdateInstance(self,host_name):
		host = self.getNodeByName(host_name)
		host.sendUpdateInstance()

	#be deleteNode called
	def getNodeByName(self, name):
		#node_list = self.getNodeList()
		for node in self.node_list:
			if node.name == name:
				return node
		return None

	#addNode message
	def getAllNodeStr(self):
		ret = ""
		for node in self.node_list:
			ret += node.name+" "
		return ret

	#clustermanager.deletecluster call
	def deleteAllNode(self):
		for node in self.node_list[:]:
			self.deleteNode(node.name)
			#print "node list:",self.node_list

	def getInfo(self):
		return [self.id, self.name]

	def checkInstanceGetVolume(self,instance_id):
		if not self.nova_client.isInstanceGetVolume(instance_id):
			message = "this instance not having volume! Instance id is %s " %instance_id
			logging.error(message)
			return False
		return True

	def checkInstancePowerOn(self,instance_id):
		if not self.nova_client.isInstancePowerOn(instance_id):
			message = "this instance is not running! Instance id is %s " % instance_id
			logging.error(message)
			return False
		return True

	def checkInstanceExist(self, instance_id):
		node_list = self.nova_client.getComputePool()
		print "node list of all compute node:",node_list
		instance_list=self.nova_client.getAllInstanceList()
		print instance_list
		for instance in instance_list:
			#print node_list
			if instance.id==instance_id:
				logging.info("Cluster--addInstance-checkInstanceExist success")
				return True
		message = "this instance is not exist. Instance id is %s. " % instance_id
		logging.error(message)
		return False

	def isProtected(self, instance_id):
		for instance in self.instance_list[:]:
			if instance.id == instance_id:
				return True
		message = "this instance is  already in the cluster. Instance id is %s. cluster id is %s .instance list is %s" % (instance_id,self.id,self.instance_list)
		logging.error(message)
		return False

	def findTargetHost(self, fail_node):
		import random
		target_list = [node for node in self.node_list if node != fail_node]
		target_host = random.choice(target_list)
		return target_host

	def updateInstance(self):
		for instance in self.instance_list:
			instance.updateInfo()
			print "instance %s update host to %s" % (instance.name, instance.host)
			#instance.host = host

	def checkInstanceHost(self,instance_id):
		host = self.nova_client.getInstanceHost(instance_id)
		for node in self.node_list[:]:
			if host == node.name:
				return host
		return None

	def liveMigrateInstance(self,instance_id):
		host = self.nova_client.getInstanceHost(instance_id)
		#for node in self.node_list:
		#if host == node.name:
		#return host
		target_host = self.findTargetHost(host)
		print "start live migrate vm from ",host,"to ",target_host.name
		final_host=self.nova_client.liveMigrateVM(instance_id,target_host.name)
		#print final_host
		return final_host

	def evacuate(self, instance, target_host, fail_node):
		self.nova_client.evacuate(instance, target_host, fail_node)

	def getProtectedInstanceList(self):
			return self.instance_list

	def getProtectedInstanceListByNode(self, node):
			ret = []
			protected_instance_list = self.getProtectedInstanceList()
			for instance in protected_instance_list:
				if instance.host == node.name:
					ret.append(instance)
			return ret
	'''
	def sendToLocal(self,ip):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('192.168.0.112', 5001))
		s.listen(5)
		# s.settimeout(5)
		while True:
			cs, addr = s.accept()
			print "addr:", addr
			cs.send(ip)
			d = cs.recv(1024)
			# print d
			if d == "get":
				cs.close()
			else:
				continue
	'''

if __name__ == "__main__":
	a = Cluster("123","name")
	list = ["compute3"]
	a.addNode(list)
	host = a.findNodeByInstance("0e0ce568-4ae3-4ade-b072-74edeb3ae58c")
	#print "h:",host


