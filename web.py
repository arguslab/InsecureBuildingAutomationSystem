################################################################################
# Web Interface
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
    context = zmq.Context()
    tc_socket = context.socket(zmq.SUB)
    tc_socket.setsockopt(zmq.SUBSCRIBE, "")
    tc_socket.bind("ipc:///tmp/feeds/0") 

    management_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        #  Wait for next request from client
        message = tc_socket.recv()
        print "WEB: ", message
    

if __name__ == "__main__":
    main()