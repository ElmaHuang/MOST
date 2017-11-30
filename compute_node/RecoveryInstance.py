import subprocess

class RecoveryInstance():
    def __init__(self):
        pass

    def rebootInstance(self,fail_instance):
        instance_name = ""
        # reboot vm
        for info in fail_instance:
            if "name" in info:
                instance_name = info.split(":")
                instance_name = instance_name[-1]
        command = "virsh reset "+ instance_name
        response = subprocess.check_output(command, shell=True)
        if "reset" in response:
            return True
        else:
            return False

    def rebuildInstance(self):
        pass
