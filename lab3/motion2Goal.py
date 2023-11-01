import pigpio
import time
import sys
import robot_controller
import signal

from sshkeyboard import listen_keyboard

pi = pigpio.pi()

robot = robot_controller.control(pi = pi)


def signal_handler(signal, frame):
    robot.set_speed_l(0)
    robot.set_speed_r(0)
    time.sleep(1)
    #http://abyz.me.uk/rpi/pigpio/python.html#callback
    robot.cancel()

    #http://abyz.me.uk/rpi/pigpio/python.html#stop
    pi.stop()
    sys.exit("Closed Motion to Goal")

signal.signal(signal.SIGINT, signal_handler)
    

while True:
    blob_in_frame = robot.blob.read()
    print(blob_in_frame)
    if len(blob_in_frame) == 0 :
        print("Lost Landmark")
        robot.set_speed_l(.25)
        robot.set_speed_r(-.25)
    else:
        if blob_in_frame[0].pt[0] < 250 :
            robot.set_speed_l(.15)
            robot.set_speed_r(-.15)
        elif blob_in_frame[0].pt[0] > 390:
            robot.set_speed_l(-.15)
            robot.set_speed_r(.15)
        else:
            print("Found Goal")
            if blob_in_frame[0].size > 450:
                print("Arrived to Goal")
                robot.set_speed_l(0)
                robot.set_speed_r(0)
                # break
            else:
                print("Moving to Goal")
                robot.set_speed_l(.5)
                robot.set_speed_r(.5)

        # print("X : ",blob_in_frame[0].pt[0], "\nY : ",blob_in_frame[0].pt[1])
robot.set_speed_l(0)
robot.set_speed_r(0)
time.sleep(1)
#http://abyz.me.uk/rpi/pigpio/python.html#callback
robot.cancel()

#http://abyz.me.uk/rpi/pigpio/python.html#stop
pi.stop()
sys.exit("Closed Motion to Goal")