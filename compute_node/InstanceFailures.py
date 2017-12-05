import libvirt
import re
import threading
import time
# import ConfigParser
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
            except Exception as e:
                print "failed to run detection method , please check libvirt is alive.exception :",str(e)
            finally:
                while True:
                    time.sleep(5)
                    if self.fail_instance != []:
                        #libvirt_connect.close()
                        try:
                            result = self.getHAInstance()
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
        event_string = self.transformDetailToString(event,detail)
        failedString = InstanceEvent.Event_failed
        print "event string :",event_string
        if event_string in failedString:
            self.fail_instance.append([domain.name(),domain.ID(),event_string])
        print "fail instance :",self.fail_instance

    def _checkNetwork(self):
        pass
        #for instance in self.instance_list:
            #print instance
        #if vm network isolation:
            #self.writelog(domain.name())

    def _checkVMWatchdog(self, connect,domain, action, opaque):
        print "domain:",domain.name()," ",domain.ID(),"action:",action
        watchdogString  = InstanceEvent.Event_watchdog_action
        if action in watchdogString:
            self.fail_instance.append([domain.name(),domain.ID(),watchdogString])

    def transformDetailToString(self,event,detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def getHAInstance(self):
        print "get ha vm"
        ha_instance = HAInstance.getInstanceList()
        print "read list :",ha_instance
        #check instance is protected
        for id,instance in ha_instance.iteritems():
            for fail_vm in self.fail_instance:
                if fail_vm[0] != instance.name:
                    del ha_instance[id]
        #any instance shoule be recovery
        if ha_instance != {}:
            for fail_instance in ha_instance:
                try:
                    result = self.recovery_vm.rebootInstance(fail_instance.id)
                    return result
                except Exception as e:
                    print str(e)
        else:#fail instance is not HA instance
            return True
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