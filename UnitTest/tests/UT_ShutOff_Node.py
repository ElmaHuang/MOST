import sys
import time

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from IPMIModule import IPMIManager

HOST = "compute3"


def run(check_timeout=60):
    ipmi_manager = IPMIManager()
    result = ipmi_manager.shutOffNode(HOST)

    while check_timeout > 0:
        power_status = ipmi_manager.getPowerStatus(HOST)
        if power_status == "Error" and result.code == "succeed":
            time.sleep(60)
            return True
        check_timeout -= 1
        time.sleep(1)
    return False
