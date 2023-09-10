# This program demonstrates usage of the servos.
# Keep the robot in a safe location before running this program,
# as it will immediately begin moving.
# See https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/ for more details.
# Import necessary libraries

import time                # For adding delays using sleep.
import Adafruit_PCA9685    # Interface with the Adafruit servo controller.
import signal              # Handle signals, especially for clean program exit.
import math                # Basic math operations

# Constants for the robot's specifications
MIN_PWM = 1.3                  # Minimum PWM value
MAX_PWM = 1.7                  # Maximum PWM value
MAX_VELOCITY = (13/6)*math.pi  # Maximal rotational velocity the robot can achieve.
MAX_RADIANS = (5/3)*math.pi    # Maximal angular displacement.
MAX_RPS = 5/6                 # Maximal rotations per second.
D_MID = 2                      # Mid-point distance, likely related to robot geometry.
r = 1.3                        # Some parameter

# Servo channel assignments
LSERVO = 0  # The channel number for the left servo.
RSERVO = 1  # The channel number for the right servo.

# Function to handle Ctrl+C interrupt
def ctrlC(signum, frame):
    """Stop both servos and exit the program."""
    print("Exiting")
    pwm.set_pwm(LSERVO, 0, 0)
    pwm.set_pwm(RSERVO, 0, 0)
    exit()

# Associate the SIGINT signal (like a Ctrl+C interrupt) with the ctrlC function.
signal.signal(signal.SIGINT, ctrlC)

# Initialize the PCA9685 servo controller
pwm = Adafruit_PCA9685.PCA9685()

# Set the frequency for PWM signals to 50Hz. This frequency is typically used for servos.
pwm.set_pwm_freq(50)

# Set the initial PWM value for both servos to represent a neutral position.
pwm.set_pwm(LSERVO, 0, math.floor(1.5 / 20 * 4096))
pwm.set_pwm(RSERVO, 0, math.floor(1.5 / 20 * 4096))

# Functions to set the servo speeds using various units
def setSpeedsPWM(pwm_left, pwm_right):
    """Set servo speeds using direct PWM values."""
    pwm.set_pwm(LSERVO, 0, math.floor(pwm_left/20 * 4096))
    pwm.set_pwm(RSERVO, 0, math.floor(pwm_right/20 * 4096))

def setSpeedsRPS(rpsLeft, rpsRight):
    """Set servo speeds using Rotations Per Second (RPS)."""
    pwm_left = (rpsLeft + 6.25) / 4.167
    pwm_right = (rpsRight + 6.25) / 4.167
    setSpeedsPWM(pwm_left, pwm_right)

def setSpeedsIPS(ipsLeft, ipsRight):
    """Set servo speeds using Inches Per Second (IPS)."""
    pwm_left = (ipsLeft + 51.05) / 34.04
    pwm_right = (ipsRight + 51.05) / 34.04
    setSpeedsPWM(pwm_left, pwm_right)

def setSpeedsVW(linear_velocity, angular_velocity, moving_time = 5):
    if angular_velocity == 0: 
        moveXV(12,linear_velocity)
        return

    radius = abs(linear_velocity/angular_velocity)

    if angular_velocity < 0:
        v_left = angular_velocity * (radius + D_MID)
        v_right = angular_velocity * (radius - D_MID)
    else:
        v_left = angular_velocity * (radius - D_MID)
        v_right = angular_velocity * (radius + D_MID)

    if v_left > MAX_VELOCITY or v_right > MAX_VELOCITY:
        print("Robot can not go that fast!")
        return
    
    if angular_velocity > 0:
        setSpeedsIPS(-v_left, v_right)
        print("Left Wheel Linear: ", v_left, "Right Wheel Linear: ", v_right)
    else:
        setSpeedsIPS(v_left, -v_right)
        print("Left Wheel Linear: ", v_left, "Right Wheel Linear: ", v_right)

    time.sleep(moving_time)
    pwm.set_pwm(LSERVO, 0, 0)
    pwm.set_pwm(RSERVO, 0, 0)

def moveXV(X, V):
    if V > MAX_VELOCITY:
        print("Robot can not go that fast!")
        return

    if X < 0:
        V = -V

    time_on = X/V
    print("Running Time: ", time_on)
    setSpeedsIPS(-V, V)
    time.sleep(abs(time_on))
    pwm.set_pwm(LSERVO, 0, 0)
    pwm.set_pwm(RSERVO, 0, 0)

#The robot starts by moving straight.
#It pauses.
#It moves in a curve.
#It pauses again.
#Finally it moves in a curve in the opposite direction

def main():
    """Main function to execute robot's motion sequence."""
    moveXV(5, 2)
    time.sleep(2)
    setSpeedsVW(3, 1)
    time.sleep(2)
    setSpeedsVW(0.5, -3)

# If this script is the main program being executed, run the main function
if __name__ == "__main__":
    try:
        main()  # Execute main robot behavior
    except KeyboardInterrupt:
        print("Program interrupted")
        ctrlC(None, None)  # Handle program interruption gracefully
