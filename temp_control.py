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


################################################################################
# CLASSES
################################################################################


################################################################################
# VARIABLES
################################################################################
setpoint = 0.0

################################################################################
# FUNCTIONS
################################################################################


################################################################################
# MAIN
################################################################################

def main():
    #Use ZMQ for local messages for simplicity
    context = zmq.Context()
    web_socket = context.socket(zmq.PUB)
    web_socket.connect("ipc:///tmp/feeds/0") 

    #We want network traffic in UDP from the sensor, so no zmq
    sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sensor_socket.bind(("0.0.0.0", 4444))

    fan_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fan_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        #  Wait for next request from client
        message, addr = sensor_socket.recvfrom(128)
        print "TEMP CONTROL: ", message, addr

        decoded_message = json.loads(message)

        if "currentTemp" in decoded_message:
            if decoded_message["currentTemp"] < setpoint:
                fan_socket.sendto(json.dumps({"enable": 0}), ("192.168.0.255", 4445))
            else:
                fan_socket.sendto(json.dumps({"enable": 1}), ("192.168.0.255", 4445))

            web_socket.send(message)

if __name__ == "__main__":
    main()
