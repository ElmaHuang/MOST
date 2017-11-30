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
        self.clearlog()
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
        libvirt_connect = self.createDetectionThread()
        while True:
            try:
                libvirt_connect.domainEventRegister(self._checkVMState,None)
                libvirt_connect.domainEventRegisterAny(None,libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,self._checkVMWatchdog,None)
                while True:
                    if not libvirt_connect.isAlive():
                        break
                    time.sleep(5)
            except Exception as e:
                print "failed to run startDetection method in VMDetector, please check libvirt is alive.exception :",str(e)
            finally:
                libvirt_connect.close()
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
        if event_string in failedString:
            self.fail_instance.append([domain.name(),domain.ID(),event_string])

    def _checkNetwork(self):
        pass
        #for instance in self.instance_list:
            #print instance
        #if vm network isolation:
            #self.writelog(domain.name())

    def _checkVMWatchdog(self, connect,domain, action, opaque):
        print "domain:",domain.name()," ",domain.ID(),"action:",action
        #watchdogString = self.config.get("vm_watchdog_event","Event_watchdog_action")
        #if action in watchdogString:
            #self.writelog(domain.name())

    def transformDetailToString(self,event,detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def clearlog(self):
        with open('./instance_fail.log', 'w'): pass
        #with open('./log/sucess.log', 'w'): pass

    def writelog(self,str):
        with open('./instance_fail.log', 'a') as f:
            f.write(str)
            f.close()

if __name__ == '__main__':
    a = InstanceFailure()
    a.start()