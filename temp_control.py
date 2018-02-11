################################################################################
# Tempurature Controller
################################################################################

################################################################################
# IMPORTS
################################################################################
import time
import zmq
import socket
import thread
import json
import threading
import os

################################################################################
# CLASSES
################################################################################


################################################################################
# VARIABLES
################################################################################
context = None
setpoint = 0.0

################################################################################
# FUNCTIONS
################################################################################

def worker():
    """
        Thread to communicate with the web proc
    """
    global context
    global setpoint

    #Setup socket for communicating with the web process
    web_socket = context.socket(zmq.SUB)
    web_socket.setsockopt(zmq.SUBSCRIBE, "")
    web_socket.bind("ipc:///tmp/feeds/1")

    while True:
        message = web_socket.recv()
        print "TEMP CONTROL: ", message

        message = json.loads(message)

        if "setpoint" in message:
            setpoint = message["setpoint"]


################################################################################
# MAIN
################################################################################

def main():
    global context
    global setpoint

    if not os.path.exists("/tmp/feeds"):
        os.makedirs("/tmp/feeds")

    #Use ZMQ for local messages for simplicity
    context = zmq.Context()
    web_socket = context.socket(zmq.PUB)
    web_socket.connect("ipc:///tmp/feeds/0") 

    #We want network traffic in UDP from the sensor, so no zmq
    sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sensor_socket.bind(("0.0.0.0", 4444))

    #Broadcast to data to the fan (roughtly modeling BACnet)
    fan_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fan_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    #Start second thread
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
    
    while True:
        #Wait for next broadcast from the sensor
        message, addr = sensor_socket.recvfrom(128)
        print "TEMP CONTROL: ", message, addr

        #Decode JSON
        decoded_message = json.loads(message)

        #Defensively check for correct value
        if "currentTemp" in decoded_message:

            #Adjust fan based on the setpoint
            if decoded_message["currentTemp"] < setpoint:
                fan_socket.sendto(json.dumps({"enable": 0}), ("192.168.0.255", 4445))
            else:
                fan_socket.sendto(json.dumps({"enable": 1}), ("192.168.0.255", 4445))

            #Forward data to web proc
            web_socket.send(message)

if __name__ == "__main__":
    main()
