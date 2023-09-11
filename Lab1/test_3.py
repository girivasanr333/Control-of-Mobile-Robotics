import robot_controller
import pigpio

pigpi = pigpio.pi() 
        
controller = robot_controller.control(pi=pigpi)
controller.straight(1000)
# controller.set_speed_r(0)
# controller.set_speed_l(0)