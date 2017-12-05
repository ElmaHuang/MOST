import subprocess
from NovaClient import NovaClient
from HAInstance import HAInstance

class RecoveryInstance(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()

    def hardRebootInstance(self,fail_instance_id):
        #instance_name = ""
        # reboot vm
        instance = self.getHAInstance(fail_instance_id)
        result = self.nova_client.hardReboot(instance.id)
        #command = "virsh reset "+ instance.name
        state = self.nova_client.getgetInstanceState(instance.id)
        if "ACTIVE" in state:
            return True
        else:
            return False

    def softReboot(self):
        pass

    def stopInstance(self):
        pass

    def pingInstance(self,id):
        instance = self.getHAInstance(id)
        ip = instance.network_provider
        try:
            response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                           universal_newlines=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def getHAInstance(self,id):
        ha_vm = HAInstance.getInstance(id)
        return ha_vm