
class Instance(object):
    def __init__(self,ha_instance):
        self.ha_instance = ha_instance
        self.id = None
        self.name = None
        self.host = None
        self.status = None
        self.network_self = []
        self.network_provider = []
        self.main()

    def main(self):
        self.id = self.ha_instance[0]
        self.name = self.ha_instance[1]
        self.host = self.ha_instance[2]
        self.status = self.ha_instance[3]
        self.update_network()

    def update_network(self):
        #{'selfservice':", "['192.168.1.8',", "'192.168.0.212']}
        self.network_self = self.ha_instance[4]["selfservice"]
        self.network_self = self.ha_instance[4]["provider"]
        #self.network

if __name__ == '__main__':
    a = Instance()


