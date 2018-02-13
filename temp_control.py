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
safety_range = 1.0

################################################################################
# FUNCTIONS
################################################################################

def worker():
    """
        Thread to communicate with the web proc
    """
    global context
    global setpoint
    global safety_range

    #Setup socket for communicating with the web process
    web_socket = context.socket(zmq.SUB)
    web_socket.setsockopt(zmq.SUBSCRIBE, "")
    web_socket.bind("ipc:///tmp/feeds/1")

    while True:
        message = web_socket.recv()
        print "TEMP CONTROL: ", message

        message = json.loads(message)

        if "setpoint" in message:
            setpoint = float(message["setpoint"])

        if "safetyRange" in message:
            safety_range = float(message["safetyRange"])


################################################################################
# MAIN
################################################################################

def main():
    global context
    global setpoint
    global safety_range

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

    alarm_socket = context.socket(zmq.PUB)
    alarm_socket.connect("ipc:///tmp/feeds/2")
    
    #Start second thread
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    fan_on = False
    alarm_on = False
    
    while True:
        #Wait for next broadcast from the sensor
        message, addr = sensor_socket.recvfrom(128)

        #Decode JSON
        decoded_message = json.loads(message)

        #Defensively check for correct value
        if "currentTemp" in decoded_message:

            err = setpoint - float(decoded_message["currentTemp"])
            print "TEMP CONTROL: err=", err

            #Adjust fan based on the setpoint
            if err > 0 and fan_on:
                fan_on = False
                fan_socket.sendto(json.dumps({"enable": 0}), ("192.168.0.255", 4445))
            elif err <= 0 and not fan_on:
                fan_on = True
                fan_socket.sendto(json.dumps({"enable": 1}), ("192.168.0.255", 4445))

            if abs(err) > safety_range and not alarm_on:
                alarm_on = True
                alarm_socket.send(json.dumps({"enable": 1}))
            elif abs(err) <= safety_range and alarm_on:
                alarm_on = False
                alarm_socket.send(json.dumps({"enable": 0}))

            #Forward data to web proc
            web_socket.send(json.dumps({"currentTemp": decoded_message["currentTemp"], "cooling": 1 if fan_on else 0, "heating": 0 if fan_on else 1, "alarm": 1 if alarm_on else 0}))

if __name__ == "__main__":
    main()
