import subprocess

class RecoveryInstance():
    def __init__(self):
        pass

    def rebootInstance(self,fail_instance):
        # [
        #  ['id', '8f3340f3-0c48-4333-98e3-96f62df41f21'],
        #  ['name', 'instance-00000346'],
        #  ['host', 'compute3'], ['status', 'ACTIVE'],
        #  ['network', 'selfservice'],
        #  ['192.168.1.8,'],
        #  ['192.168.0.212']
        # ]
        instance_name = ""
        # reboot vm
        for info in fail_instance:
            if "name" in info[0]:
                instance_name = info[1]
                #instance_name = instance_name[-1]
        command = "virsh reset "+ instance_name
        response = subprocess.check_output(command, shell=True)
        if "reset" in response:
            return True
        else:
            return False

    def rebuildInstance(self):
        pass
