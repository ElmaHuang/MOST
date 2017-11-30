import threading
import socket
import xmlrpclib
import subprocess

class recvIPThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.s.bind(('192.168.0.115',5001))
        self.s.listen(5)
        self.authUrl = "http://user:0928759204@192.168.0.112:61209"
        self.server = xmlrpclib.ServerProxy(self.authUrl)
        self.host = subprocess.check_output(['hostname']).strip()
        self.ha_instance_list = []

    def run(self):
        while True:
            cs,addr = self.s.accept()
            print "addr:", addr
            d = cs.recv(1024)
            print d
            if d == "update instance":
                self.updateHAInstance()

    def updateHAInstance(self):
        self.clearlog()
        instance_list = self.getInstanceFromController()
        for instance in instance_list[:]:
            str = "id:"+instance[0]+" name:"+instance[1]+" host:"+instance[2]+" status:"+instance[3]+" network:"+instance[4]
            self.writelog(str)
            
    def getInstanceFromController(self):
        host_instance = []
        cluster_list = self.server.listCluster()
        for cluster in cluster_list:
            clusterId = cluster[0]
            instance_list = self.server.listInstance(clusterId,False)["instanceList"]
            print "HA instacne list:",instance_list
            for instance in instance_list:
                if self.host in instance[2] :
                    host_instance.append(instance)
        return host_instance

    def clearlog(self):
        with open('./HAInstance', 'w'): pass
        #with open('./log/sucess.log', 'w'): pass

    def writelog(self,str):
        with open('./HAInstance', 'a') as f:
            f.write(str)
            f.close()