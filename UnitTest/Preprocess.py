#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import time

import Instance

III_SERVER_SUCCESS_MSG = "start/running"
# III_SERVER_FAIL_MSG = "stop/waiting"
III_SERVER_START_COMMAND = "service HASSd start"
III_SERVER_STATUS_COMMAND = "service HASSd status"
MOST_HASS_PATH = "/home/controller/Desktop/MOST/HASS/"
MOST_SERVER_START_COMMAND = "python Hass.py &"


def do():
    pass


def server_start(iii_support=True):
    if iii_support:
        _local_exec(III_SERVER_START_COMMAND)
        status = _local_exec(III_SERVER_STATUS_COMMAND)
        if III_SERVER_SUCCESS_MSG in status:
            raise Exception("Server not ready !")
    else:
        _local_exec(MOST_SERVER_START_COMMAND,False)

    print "SERVER READY"
    time.sleep(1)


def create_with_provider_instance():
    return Instance.create_provider_instance()


def create_with_selfservice_instance():
    return Instance.create_selfservice_instance()


def _deleteInstance():
    return Instance.delete()


def _local_exec(cmd, iii=True):
    if iii == True:
        p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, shell=False, stdout=open(os.devnull, 'w'))
    else:
        p = subprocess.Popen(cmd.split(), cwd=MOST_HASS_PATH, stdin=subprocess.PIPE, shell=False,
                             stdout=open(os.devnull, 'w'))
    return p.communicate()


def test():
    print "test"


if __name__ == '__main__':
    pass
    # _createInstance()
    # _deleteInstance()
