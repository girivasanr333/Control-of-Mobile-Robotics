import time
import robot_controller
import pigpio

# Initialize the pigpio library
pigpi = pigpio.pi()

# Initialize the robot controller
controller = robot_controller.control(pi=pigpi)

max_speed = 0.4
min_speed = 0.35

def get_saturated_speed(speed):
    if speed > max_speed:
        return max_speed
    elif speed < min_speed:
        return min_speed
    else:
        return speed

def turn_90_degrees(direction="right"):
    """Turns the robot 90 degrees to the specified direction."""
    if direction == "right":
        controller.set_speed_l(0.3)
        controller.set_speed_r(-0.3)
    else:
        controller.set_speed_l(-0.3)
        controller.set_speed_r(0.3)
    time.sleep(0.1)  # Adjust as necessary for 90-degree turn
    controller.set_speed_l(0)
    controller.set_speed_r(0)

def wall_following(controller, Kp_side=0.1):
    """Make the robot follow the wall and maintain a distance."""
    print(f"Starting wall following with Kp_side: {Kp_side}")

    set_distance = 20  # Set distance from the wall

    start_time = time.time()
    current_time = start_time

    while current_time - start_time < 30:
        # Retrieve distance sensor readings
        time.sleep(0.1)
        front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()
        print(f"Front Distance: {front_distance}, Right Distance: {right_distance}, Left Distance: {left_distance}")

        # Check front sensor and turn if too close
        if front_distance < 35:
            print("Front obstacle detected, turning right!")
            turn_90_degrees("right")
            continue

        error_left = left_distance - set_distance
        error_right = right_distance - set_distance

        print(f"Left Error: {error_left}, Right Error: {error_right}")

        # Apply proportional control for side walls
        left_control = Kp_side * error_left
        right_control = Kp_side * error_right
        print(f"Left Control Adjustment: {left_control}, Right Control Adjustment: {right_control}")

        l_speed = get_saturated_speed(-1*left_control + right_control)
        r_speed = get_saturated_speed(left_control - right_control)

        controller.set_speed_l(l_speed)
        controller.set_speed_r(r_speed)

        current_time = time.time()
        print(f"time: {current_time - start_time}")

        print(f"Left Motor Speed: {l_speed}, Right Motor Speed: {r_speed}")

    controller.set_speed_l(0)
    controller.set_speed_r(0)


# Test the wall following function
Kp_side = 0.1  # Replace with the best Kp value from your tests
wall_following(controller=controller, Kp_side=Kp_side)
