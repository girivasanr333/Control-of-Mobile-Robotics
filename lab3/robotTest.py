import pigpio
import time

import robot_controller

pi = pigpio.pi()

robot = robot_controller.control(pi = pi)

 
ticks_l = []
ticks_r = []
start_time = time.time()

# try:
# 	robot.turn(90)
# except Exception as e:
# 	raise
# else:
# 	pass
# finally:
# 	robot.set_speed_l(0)
# 	robot.set_speed_r(0)
# 	pass

# robot.set_speed_l(1)
# robot.set_speed_r(1)
# time.sleep(1)
# robot.set_speed_l(0)
# robot.set_speed_r(0)
# time.sleep(3)
# # robot.set_speed_l(-.5)
# # robot.set_speed_r(-.5)
# # time.sleep(1)
# # robot.set_speed_l(0)
# # robot.set_speed_r(0)
# # time.sleep(3)
# robot.set_speed_l(-.25)
# robot.set_speed_r(-.25)
# time.sleep(4)
# robot.set_speed_l(0)
# robot.set_speed_r(0)

for i in range(50):
    print(robot.blob.read())
    time.sleep(.5)


#http://abyz.me.uk/rpi/pigpio/python.html#callback
robot.cancel()

#http://abyz.me.uk/rpi/pigpio/python.html#stop
pi.stop()