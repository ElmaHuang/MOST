import libvirt
import socket
import threading
import time
# import ConfigParser
import InstanceEvent
from RecoveryInstance import RecoveryInstance

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
                        libvirt_connect.close()
                        self.getHAInstance()
                    if not libvirt_connect.isAlive():
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
        ha_instance = self.readlog()
        print "read list :",ha_instance
        for instance in ha_instance[:]:
            for fail_vm in self.fail_instance:
                if fail_vm[0] not in instance:
                    ha_instance.remove(instance)
        if ha_instance != []:
            for fail_instance in ha_instance[:]:
                try:
                    result = self.recovery_vm.rebootInstance(fail_instance)
                    if result != True:
                        raise Exception("reset vm fail")
                except Exception as e:
                    print str(e)

    def readlog(self):
        ha_instance = []
        with open('./HAInstance', 'r') as ff:
            for lines in ff:
                instance = lines.split(" ")
                ha_instance.append(instance)
        ff.close()
        return ha_instance

if __name__ == '__main__':
    a = InstanceFailure()
    a.start()