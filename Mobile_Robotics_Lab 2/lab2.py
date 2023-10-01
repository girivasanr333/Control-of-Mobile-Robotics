import statistics
import time
import numbers
import math
import pigpio
import robot_controller
# Robot sensors and motors
import board
import adafruit_tca9548a
import adafruit_vl53l4cd
import adafruit_bno055

pigpi = pigpio.pi()
left = "left"
right = "right"
straight = "straight"

# Initialize the robot controller
controller = robot_controller.control(pi=pigpi)

def  autonomous_move(controller, T, d):
    """Move the robot autonomously based on distance sensor readings."""
    controller.sampling_time = T
    controller.set_speed_l(0.4)
    controller.set_speed_r(0.4)

    thresholdReached = False
    while not thresholdReached:
        start_time_each_loop = time.time()

        # Read the distance sensors
        # front_distance = controller.front_ds.get_distance()
        # right_distance = controller.right_ds.get_distance()
        # left_distance = controller.left_ds.get_distance()
        # rear_distance = controller.rear_ds.get_distance()

        front_distance,  right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()

        print(front_distance)

        
        # Define a threshold distance below which robot will consider taking action (e.g., 20 cm).
        threshold = d
        
        if front_distance <= threshold:
            # If an obstacle is detected in the front, the robot should stop or turn.
            controller.set_speed_l(0)
            controller.set_speed_r(0)
            thresholdReached = True
            #print(front_distance)
           
        # elif right_distance < threshold:
        #     # If an obstacle is detected on the right, turn left.
        #     controller.set_speed_l(-50)
        #     controller.set_speed_r(50)
          
        # elif left_distance < threshold:
        #     # If an obstacle is detected on the left, turn right.
        #     controller.set_speed_l(50)
        #     controller.set_speed_r(-50)
        #     time.sleep(1)
        else:
            # If no obstacles are detected, move forward.
            print("Distance not reached")

            controller.set_speed_l(0.4)
            controller.set_speed_r(0.4)
        
        time.sleep(controller.sampling_time - ((time.time() - start_time_each_loop) % controller.sampling_time))

autonomous_move(controller=controller, T=0.001, d= 60)

# front_distance,  right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()


# print(controller.right_ds.distance)

print("2")
