import threading
import socket
import xmlrpclib

class recvIPThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.s.bind(('192.168.0.115',5001))
        self.s.listen(5)
        self.authUrl = "http://user:0928759204@192.168.0.112:61209"
        self.server = xmlrpclib.ServerProxy(self.authUrl)

    def run(self):
        while True:
            cs,addr = self.s.accept()
            print "addr:", addr
            d = cs.recv(1024)
            print d
            if d == "update instance":
                self.getInstanceFromController()

    def getInstanceFromController(self):
        host_instance = []
        cluster_list = self.server.listCluster()
        for cluster in cluster_list:
            clusterId = cluster[0]
            instance_list = self.server.listInstance(clusterId)["instanceList"]
            for instance in instance_list:
                if instance[2] == self.host:
                    host_instance.append(instance)
        return host_instance

    def installWatchdog(self):
        pass

    def checkVMNetwork(self):
        pass
