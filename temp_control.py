################################################################################
# Tempurature Controller
################################################################################

################################################################################
# IMPORTS
################################################################################
import time
import zmq
import socket

################################################################################
# CLASSES
################################################################################


################################################################################
# VARIABLES
################################################################################


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

    while True:
        #  Wait for next request from client
        message, addr = sensor_socket.recvfrom(128)
        print "TEMP CONTROL: ", message, addr
    
        web_socket.send(message)    

if __name__ == "__main__":
    main()