import xmlrpclib

import Postprocess
import Preprocess

no_auth = ""


def run():
    try:
        Preprocess.server_start(False)
        server = xmlrpclib.ServerProxy(no_auth)
        response = server.test_auth_response()
        if response == "auth success":
            return False
        return True
    except Exception as e:
        print str(e)
        return True
    finally:
        Postprocess.server_stop(False)
