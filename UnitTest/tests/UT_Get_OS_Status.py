import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from IPMIModule import IPMIManager

HOST = "compute3"


def run():
    ipmi_manager = IPMIManager()
    try:
        result = ipmi_manager.getOSStatus(HOST)
        if result == "OK":
            return True
        else:
            return False
    except:
        return False
