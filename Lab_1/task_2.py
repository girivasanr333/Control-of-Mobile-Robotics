# See https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/ for more details.
import time
import math
from tkinter import W
import RPi.GPIO as GPIO  # Library to control Raspberry Pi GPIO pins.
import Adafruit_PCA9685  # Library for the Adafruit servo controller.
import signal  # Library for handling signals like Ctrl+C.
import task_1  # Custom library.
from task_1 import MAX_PWM, MIN_PWM, MAX_VELOCITY, MAX_RADIANS, MAX_RPS, D_MID  # Import constants from task_1.

# This function stops the robot gracefully when Ctrl+C is pressed.
def ctrlC(signum, frame):
    """Gracefully exit the program."""
    print("Exiting")
    GPIO.cleanup()  # Clean up GPIO to a safe state
    exit()

# Attach the function to the Ctrl+C signal interrupt.
signal.signal(signal.SIGINT, ctrlC)

######################################################################
# Functions related to the robot's encoders
#####################################################################

# Encoder pin definitions
LENCODER = 17  # Left encoder pin number.
RENCODER = 18  # Right encoder pin number.

class Encoders():
    """A class to represent and manage robot encoders."""

    def __init__(self) -> None:
        """Initialize the encoder tick values."""
        self.left_ticks = 0
        self.right_ticks = 0

    def reset(self):
        """Reset encoder tick values."""
        self.left_ticks = 0
        self.right_ticks = 0

    def increase_left(self):
        """Increase left encoder tick count by 1."""
        self.left_ticks += 1

    def increase_right(self):
        """Increase right encoder tick count by 1."""
        self.right_ticks += 1

    def get_left(self):
        """Get left encoder tick count."""
        return self.left_ticks

    def get_right(self):
        """Get right encoder tick count."""
        return self.right_ticks

# Create an encoder instance.
encoder = Encoders()

def onLeftEncode(pin):
    """Callback when left encoder detects a tick (rising edge)."""
    encoder.increase_left()

def onRightEncode(pin):
    """Callback when right encoder detects a tick (rising edge)."""
    encoder.increase_right()

# Set the pin numbering scheme.
GPIO.setmode(GPIO.BCM)

# Setup encoder pins as input with pull-up resistors.
GPIO.setup(LENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Add rising edge detection to encoder pins.
GPIO.add_event_detect(LENCODER, GPIO.RISING, onLeftEncode)
GPIO.add_event_detect(RENCODER, GPIO.RISING, onRightEncode)

def resetCounts():
    """Reset tick counts for both encoders."""
    encoder.reset()

def getCounts():
    """Return the tick counts for both encoders."""
    return (encoder.get_left(), encoder.get_right())

def getSpeeds():
    """Calculate and return the speeds of both wheels in inches per second."""
    current_left = encoder.get_left()
    current_right = encoder.get_right()
    time.sleep(1)

    # Each tick is pi/16 radians. Multiply ticks over one second by pi/16 to get angular velocity in rad/s
    left_angularv = ((encoder.get_left() - current_left) * math.pi) / 16
    right_angularv = ((encoder.get_right() - current_right) * math.pi) / 16
    
    # Find linear velocity of each wheel by using [v = wr]
    left_linear = left_angularv * 1.3
    right_linear = right_angularv * 1.3
    return (left_linear,right_linear)

def turnRV(R:int, V:int): 
    """Make the robot move in a circle of radius R at a linear velocity of V."""
    w = V/R
    circumference = 2* math.pi * R
    circle_time = abs(circumference/V)
    print("Circumference:  ", circumference,"Circle Time: ", circle_time)
    task_1.setSpeedsVW(V,w,circle_time)
    print(getCounts())


# Uncomment below lines to test the `turnRV` function and exit.
# turnRV(5,-1)
# exit()
