import time
import pigpio
import robot_controller

# Constants
FRONT_TARGET_DISTANCE = 0.5  # target stopping distance from the front wall in meters
SIDE_MIN_DISTANCE = 0.3  # minimum distance to maintain from side walls in meters
MAX_TIME = 30  # Maximum running time in seconds

# Initialize
pigpi = pigpio.pi()
controller = robot_controller.control(pi=pigpi)


def autonomous_move(controller, T, Kp_front, Kp_side):
    """Move the robot autonomously using P control based on distance sensor readings."""
    controller.sampling_time = T

    start_time = time.time()

    while time.time() - start_time < MAX_TIME:
        loop_start_time = time.time()

        # Read the distance sensors
        front_distance, right_distance, left_distance = controller.get_primary_distance_sensor_readings()

        # Proportional control for front sensor
        front_error = FRONT_TARGET_DISTANCE - front_distance
        front_speed = Kp_front * front_error
        front_speed = min(max(front_speed, 0), 0.4)  # Limit speed between 0 and 0.4

        # Proportional control for side sensors
        right_error = right_distance - SIDE_MIN_DISTANCE
        left_error = left_distance - SIDE_MIN_DISTANCE
        right_speed_adjustment = Kp_side * right_error
        left_speed_adjustment = Kp_side * left_error

        # Calculate the adjusted speeds for left and right motors
        left_motor_speed = front_speed + left_speed_adjustment
        right_motor_speed = front_speed + right_speed_adjustment

        # Set the motor speeds
        controller.set_speed_l(left_motor_speed)
        controller.set_speed_r(right_motor_speed)

        print(f"Front Distance: {front_distance} m, Right Distance: {right_distance} m, Left Distance: {left_distance} m")
        
        # Sleep for the remaining time in the sampling period
        time.sleep(T - ((time.time() - loop_start_time) % T))


# Test with different Kp values
kp_values = [0.1, 0.5, 1.0, 2.0, 2.5, 5.0]
for kp in kp_values:
    print(f"\nRunning with Kp_front = {kp} and Kp_side = {kp}\n")
    autonomous_move(controller=controller, T=0.01, Kp_front=kp, Kp_side=kp)

