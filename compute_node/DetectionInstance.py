import threading
import libvirt
import  time
import InstanceEvent

class LibvirtDetetion(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.creatLibvirtListen()
        connect = libvirt.openReadOnly('qemu:///system')
        if connect == None:
            print "failed to open connection to qemu:///system"
        # while True:
        try:
            connect.domainEventRegister(self._checkVMState, None)
            connect.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG, self._checkVMWatchdog, None)
        except Exception as e:
            print "failed to run startDetection method in VMDetector, please check libvirt is alive.exception :", str(e)
        finally:
            # self.close()
            # connect.close()
            time.sleep(5)

    def creatLibvirtListen(self):
        try:
            # set event loop thread
            libvirt.virEventRegisterDefaultImpl()
            eventLoopThread = threading.Thread(target=self.__virEventLoopNativeRun, name="libvirtEventLoop")
            eventLoopThread.setDaemon(True)
            eventLoopThread.start()
            # open the connection to self qemu
        except Exception as e:
            return str(e)

    def __virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def _checkVMState(self, connect, domain, event, detail, opaque):
        #event:cloume,detail:row
        print "domain name :",domain.name()," domain id :",domain.ID(),"event:",event,"detail:",detail
        event_string = self.transformDetailToString(event,detail)
        failedString = InstanceEvent.Event_failed
        if event_string in failedString:
            self.writelog(domain.name())
        #return True

    def checkVMNetwork(self):
        pass

    def transformDetailToString(self, event, detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def _checkVMWatchdog(self, connect,domain, action, opaque):
        print "domain:",domain.name()," ",domain.ID(),"action:",action
        #watchdogString = self.config.get("vm_watchdog_event","Event_watchdog_action")
        #if action in watchdogString:
            #self.writelog(domain.name())
