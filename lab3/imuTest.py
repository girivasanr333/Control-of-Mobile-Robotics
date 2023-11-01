import pigpio
import time
import signal

import robot_controller

def handler(signum, frame):
    
    robot.set_speed_l(0)
    robot.set_speed_r(0)
    #http://abyz.me.uk/rpi/pigpio/python.html#callback
    robot.cancel()

    #http://abyz.me.uk/rpi/pigpio/python.html#stop
    pi.stop()
    exit()
 
signal.signal(signal.SIGINT, handler)


pi = pigpio.pi()

robot = robot_controller.control(pi = pi)

start_time = time.time()

robot.set_speed_l(0)
robot.set_speed_r(0)

for i in range(8):
    print("Starting:"+str(robot.imu.euler[0]))

    robot.turn(90)

    robot.straight(300)

    print("Ending:"+str(robot.imu.euler[0]))

    time.sleep(2)





robot.set_speed_l(0)
robot.set_speed_r(0)
#http://abyz.me.uk/rpi/pigpio/python.html#callback
robot.cancel()

#http://abyz.me.uk/rpi/pigpio/python.html#stop
pi.stop()