import socket
import sys
import time

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from IPMIModule import IPMIManager

HOST = "compute3"
PORT = 2468


def run(check_timeout=300):
    ipmi_manager = IPMIManager()
    result = ipmi_manager.rebootNode(HOST)
    time.sleep(5)  # wait node to reboot
    while check_timeout > 0:
        response = _check_boot_up()
        print response
        if response == "OK" and result.code == "succeed":
            time.sleep(5)
            return True
        time.sleep(1)
    return False


def _check_boot_up():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.settimeout(0.5)
    sock.connect((HOST, PORT))
    try:
        line = "polling request"
        sock.sendall(line)
        data, addr = sock.recvfrom(1024)
        return data
    except Exception as e:
        print str(e)
        return "Error"
