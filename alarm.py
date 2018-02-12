################################################################################
# Alarm
################################################################################

################################################################################
# IMPORTS
################################################################################
import threading
import zmq
import socket
import json
import os
from gpio import *

################################################################################
# CLASSES
################################################################################


################################################################################
# VARIABLES
################################################################################
alarm_status = 0
g = gpio(9)
led_status = 0

################################################################################
# FUNCTIONS
################################################################################
def blink():
    """
        Periodically toggle the alarm led
    """
    global alarm_status
    global g
    global led_status
    
    if not alarm_status:
        #toggle
        led_status ^= 1  
        g.set_value(led_status)

    threading.Timer(0.1, blink).start()


################################################################################
# MAIN
################################################################################

def main():
    global alarm_status
    global g

    if not os.path.exists("/tmp/feeds"):
        os.makedirs("/tmp/feeds")

    context = zmq.Context()
    tc_socket = context.socket(zmq.SUB)
    tc_socket.setsockopt(zmq.SUBSCRIBE, "")
    tc_socket.bind("ipc:///tmp/feeds/2") 

    g.set_direction(gpio.Direction.Output)
    g.set_value(led_status)
    blink()

    while True:
        #  Wait for next request from client
        message = tc_socket.recv()
        print "ALARM: ", message

        message = json.loads(message)
        if "enable" in message:    
            alarm_status = message["enable"]

if __name__ == "__main__":
    main()
