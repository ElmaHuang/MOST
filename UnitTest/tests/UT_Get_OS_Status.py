from MOST.IPMIModule import IPMIManager

HOST = "compute3"

def run():
	ipmi_manager = IPMIManager()
	try:
		result = ipmi_manager.getOSStatus(HOST)
		if result:
			return True
		else:
			return False
	except:
		return False