import subprocess
from HAInstance import HAInstance

class RecoveryInstance(object):
    def __init__(self):
        pass

    def rebootInstance(self,fail_instance_id):
        #instance_name = ""
        # reboot vm

        instance = HAInstance.getInstance(fail_instance_id)
        command = "virsh reset "+ instance.name
        response = subprocess.check_output(command, shell=True)
        if "reset" in response:
            return True
        else:
            return False

    def rebuildInstance(self):
        pass
