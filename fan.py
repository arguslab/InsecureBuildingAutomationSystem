################################################################################
# Fan
################################################################################

################################################################################
# IMPORTS
################################################################################
import socket
import gpio

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
    #We want network traffic in UDP from the TC
    sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sensor_socket.bind(("0.0.0.0", 4445))

    g = GPIO(9)

    while True:
        #  Wait for next request from client
        message, addr = sensor_socket.recvfrom(128)
        print "FAN: ", message, addr

        g.write(1)
    

if __name__ == "__main__":
    main()
