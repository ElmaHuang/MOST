import libvirt
import subprocess
import threading
import time
# import ConfigParse
import InstanceEvent
from RecoveryInstance import RecoveryInstance
from HAInstance import HAInstance

class InstanceFailure(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.host = host
        self.recovery_vm = RecoveryInstance()
        self.fail_instance = []
        '''
        while True:
            self._startDetection()
            time.sleep(2)
        '''

    def __virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def run(self):
        while True:
            try:
                libvirt_connect = self.createDetectionThread()
                libvirt_connect.domainEventRegister(self._checkVMState,None)
                libvirt_connect.domainEventRegisterAny(None,libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,self._checkVMWatchdog,None)
                #self._checkNetwork()
            except Exception as e:
                print "failed to run detection method , please check libvirt is alive.exception :",str(e)
            finally:
                while True:
                    time.sleep(5)
                    if self.fail_instance != []:
                        #libvirt_connect.close()
                        try:
                            result = self.recoverInstance()
                            if not result:
                                print "recovery "+str(self.fail_instance) +"fail or the instance is not HA instance."
                        except Exception as e :
                            print str(e)
                        finally:
                            self.fail_instance = []
                    elif not libvirt_connect.isAlive():
                        break
                #time.sleep(5)

    def createDetectionThread(self):
        try:
            # set event loop thread
            libvirt.virEventRegisterDefaultImpl()
            eventLoopThread = threading.Thread(target=self.__virEventLoopNativeRun, name="libvirtEventLoop")
            eventLoopThread.setDaemon(True)
            eventLoopThread.start()

            connect = libvirt.openReadOnly('qemu:///system')
            if connect == None:
                print "failed to open connection to qemu:///system"
            else:
                return connect
        except Exception as e:
            return str(e)

    def _checkVMState(self, connect, domain, event, detail, opaque):
        #event:cloume,detail:row
        print "domain name :",domain.name()," domain id :",domain.ID(),"event:",event,"detail:",detail
        recovery_type = "State"
        event_string = self.transformDetailToString(event,detail)
        failedString = InstanceEvent.Event_failed
        print "state event string :",event_string
        if event_string in failedString:
            self.fail_instance.append([domain.name(),event_string,recovery_type])
        print "fail instance--State:",self.fail_instance

    def _checkNetwork(self):
        recovery_type = "Network"
        ha_instance = HAInstance.getInstanceList()
        for id ,instance in ha_instance.iteritems():
            ip = instance.network_provider
            try:
                response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                      universal_newlines=True)
            except subprocess.CalledProcessError:
                self.fail_instance.append([instance.name,ip,recovery_type])

    def _checkVMWatchdog(self, connect,domain, action, opaque):
        print "domain name:",domain.name()," domain id:",domain.ID(),"action:",action
        recovery_type = "Watchdog"
        watchdogString  = InstanceEvent.Event_watchdog_action
        print "watchdog event string:",watchdogString
        if action in watchdogString:
            self.fail_instance.append([domain.name(),watchdogString,recovery_type])
        print "fail instance--WD:",self.fail_instance

    def transformDetailToString(self,event,detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def recoverInstance(self):
        print "get ha vm"
        ha_instance = HAInstance.getInstanceList()
        print "read list :",ha_instance
        #check instance is protected
        self.checkRecoveryVM(ha_instance)
        #any instance shoule be recovery
        if self.fail_instance != []:
            for fail_instance in self.fail_instance:
                try:
                    result = self.recovery_vm.recoverInstance(fail_instance)
                    return result
                except Exception as e:
                    print str(e)
        else:#fail instance is not HA instance
            return True

    def checkRecoveryVM(self,ha_instance):
        #find all fail_vm in self.fail_instacne is ha vm or not
        if ha_instance == {}:
            return
        for fail_vm in self.fail_instance[:]:
            for id,instance in ha_instance.iteritems():
                if fail_vm[0] not in instance.name:
                    self.fail_instance.remove(fail_vm)

    '''
    def readlog(self):
        ha_instance = []
        with open('./HAInstance.py', 'r') as ff:
            for lines in ff:
                instances = lines.split("\n")
                #[['id:8f3340f3-0c48-4333-98e3-96f62df41f21', 'name:instance-00000346', 'host:compute3', 'status:ACTIVE', "network:{'selfservice':", "['192.168.1.8',", "'192.168.0.212']}\n"]]
                for instance in instances:
                    #id:219046ce-1c1e-4a73-ac53-4cacafd08e79 name:instance-00000342 host:compute3 status:ACTIVE network:{'provider': ['192.168.0.207']}
                    instance = self._splitString(instance)
                    if instance != []:ha_instance.append(instance)
        ff.close()
        return ha_instance

    def _splitString(self,string):
        instance = []
        inst = re.sub('[\[\]{}\'"]', '', string)
        #['id:8f3340f3-0c48-4333-98e3-96f62df41f21', ' name:instance-00000346', ' host:compute3', ' status:ACTIVE', ' network:selfservice:', ' 192.168.1.8', '', ' 192.168.0.212']
        inst = "".join(inst)
        inst = inst.split(" ")
        for str in inst:
            str = re.split(r'[:\s]\s*', str)
            for c in str :
                if c =="":
                    str.remove(c)
            if str != []:instance.append(str)
            #[
            # ['id', '8f3340f3-0c48-4333-98e3-96f62df41f21'],
            # ['name', 'instance-00000346'],
            # ['host', 'compute3'],
            # ['status', 'ACTIVE'],
            # ['network', 'selfservice'],
            # ['192.168.1.8'],
            # ['192.168.0.212']
            # ]
        return instance
    '''

if __name__ == '__main__':
    a = InstanceFailure()
    a.start()
    #a._splitString("[['id:8f3340f3-0c48-4333-98e3-96f62df41f21', 'name:instance-00000346', 'host:compute3', 'status:ACTIVE', \"network:{'selfservice':\", \"['192.168.1.8',\", \"'192.168.0.212']}")