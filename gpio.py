################################################################################
# GPIO Manipulator
################################################################################

################################################################################
# IMPORTS
################################################################################

################################################################################
# CLASSES
################################################################################
class GPIO():
    class Direction(Enum):
        Input = "in"
        Output = "out"

    direction_f = None
    value_f = None

    def __init__(pin):
        with open("/sys/class/gpio/export", "w") as f:
            f.write(str(pin))
            path = "/sys/class/gpio/gpio" + str(pin) + "/"
            direction_f = open(path + "direction", "w")
            value_f = open(path + "value", "rw")
    
    def set_direction(dir):
        if dir != Direction.Input and dir != Direction.Output:
            return
        direction_f.write(dir)

    def set_value(val):
        value_f.write(val)

################################################################################
# VARIABLES
################################################################################


################################################################################
# FUNCTIONS
################################################################################
