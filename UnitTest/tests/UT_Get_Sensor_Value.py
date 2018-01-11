import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from IPMIModule import IPMIManager

HOST = "compute3"
TYPE = ["Inlet Temp"]


def run():
    ipmi_manager = IPMIManager()
    result = ipmi_manager.getNodeInfoByType(HOST, TYPE)
    if result.code == "succeed":
        return True
    else:
        return False
