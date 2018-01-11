import socket
import sys
import time

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from IPMIModule import IPMIManager

HOST = "compute4"
PORT = 2468


def run(check_timeout=300):
    ipmi_manager = IPMIManager()
    result = ipmi_manager.startNode(HOST)
    print "wait to %s boot up" % HOST
    time.sleep(130)
    response = _check_boot_up(check_timeout)
    print response
    if response == "OK" and result.code == "succeed":
        return True
        # time.sleep(5)
    return False


def _check_boot_up(check_timeout):
    print "strat check detectionagent in %s" % HOST
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.settimeout(0.5)
    sock.connect((HOST, PORT))
    while check_timeout > 0:
        try:
            line = "polling request"
            sock.sendall(line)
            data, addr = sock.recvfrom(1024)
            print "data:", data
            if data == "OK":
                return data
            else:
                time.sleep(1)
                check_timeout -= 1
                continue
        except Exception as e:
            print str(e)
            time.sleep(1)
            check_timeout -= 1
            continue
    return "Error"
