import pigpio
import time
import sys
import robot_controller

from sshkeyboard import listen_keyboard



pi = pigpio.pi()

robot = robot_controller.control(pi = pi)


def press(key):
    if key == 'up':
        robot.set_speed_l(1)
        robot.set_speed_r(1)
    if key == 'down':
        robot.set_speed_l(-1)
        robot.set_speed_r(-1)
    if key == 'right':
        robot.set_speed_l(.5)
        robot.set_speed_r(-.5)
    if key == 'left':
        robot.set_speed_l(-.5)
        robot.set_speed_r(.5)
    if key == 'q':
        robot.set_speed_l(0)
        robot.set_speed_r(0)
        #http://abyz.me.uk/rpi/pigpio/python.html#callback
        robot.cancel()

        #http://abyz.me.uk/rpi/pigpio/python.html#stop
        pi.stop()
        sys.exit("Closed RC Control") 

def release(key):
    robot.set_speed_l(0)
    robot.set_speed_r(0)

print("Starting RC Control Listening")

listen_keyboard(
    on_press=press,
    on_release=release,
)