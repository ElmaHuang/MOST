
class HAInstance():
    instance_list = None

    @staticmethod
    def init():
        HAInstance.instance_list = {}

    @staticmethod
    def addInstance(ha_instance):
        id = ha_instance.id
        HAInstance.instance_list[id] = ha_instance

    @staticmethod
    def updateInstance():
        if HAInstance.instance_list != {}:
            for obj in HAInstance.instance_list[:]:
                del obj

    @staticmethod
    def getInstanceList():
        return HAInstance.instance_list


