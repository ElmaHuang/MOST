import subprocess
from NovaClient import NovaClient
from HAInstance import HAInstance

class RecoveryInstance(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()
        self.vm_name = None
        self.fail_state = None
        self.recovery_type = None

    def recoverInstance(self,fail_vm):
        #fail_vm = ['instance-00000344', 43, 'Failed']
        self.vm_name = fail_vm[0]
        self.fail_state = fail_vm[1]
        self.recovery_type = fail_vm[2]
        self.findFailure()

    def findFailure(self):
        if "State" or "Watchdog" in self.recovery_type:
            self.hardRebootInstance(self.vm_name)
            #self.softReboot()
        elif "Network" in self.recovery_type:
            self.softReboot()
            self.pingInstance(self.vm_name)

    def hardRebootInstance(self,fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        self.nova_client.hardReboot(instance.id)
        #command = "virsh reset "+ instance.name
        self.checkState(instance.id)

    def softReboot(self,fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        self.nova_client.softReboot(instance.id)
        self.checkState(instance.id)

    def pingInstance(self,name):
        instance = self.getHAInstance(name)
        ip = instance.network_provider
        try:
            response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,universal_newlines=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def getHAInstance(self,name):
        ha_vm = HAInstance.getInstance(name)
        return ha_vm

    def checkState(self,id,check_timeout = 60):
        while check_timeout > 0:
            state = self.nova_client.getInstanceState(id)
            if "ACTIVE" in state:
                return True
            else:
                check_timeout -=1
        return False
