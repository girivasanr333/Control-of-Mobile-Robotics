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

def turn_degrees(direction="right", degrees=90):
    """Turns the robot a certain degrees to the specified direction."""
    turn_duration = 0.75 * (degrees/90)
    if direction == "right":
        controller.set_speed_l(0.3)
        controller.set_speed_r(-0.3)
    else:
        controller.set_speed_l(-0.3)
        controller.set_speed_r(0.3)
    time.sleep(turn_duration)
    controller.set_speed_l(0)
    controller.set_speed_r(0)

def move_forward(units=21):
    """Move the robot forward for a certain number of units."""
    # Assuming each unit takes 0.1 seconds to cover at max speed.
    # Adjust this based on the robot's speed and the definition of a 'unit'.
    duration = units * 0.1
    controller.set_speed_l(max_speed)
    controller.set_speed_r(max_speed)
    time.sleep(duration)
    controller.set_speed_l(0)
    controller.set_speed_r(0)

def wall_following(controller, Kp_side=0.1):
    """Make the robot follow the wall, make decisions based on sensor readings."""
    print(f"Starting wall following with Kp_side: {Kp_side}")

    while True:
        # Retrieve distance sensor readings
        time.sleep(0.1)
        front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()
        print(f"Front Distance: {front_distance}, Right Distance: {right_distance}, Left Distance: {left_distance}")

        # Decision-making based on sensor readings
        if front_distance <= 26:  
            if 40 < right_distance <= 130:
                print("Front obstacle detected and right space is between 40 and 75, turning right!")
                turn_degrees("right")
                move_forward(21)  # Move 10 units forward after turning
                continue
            elif 40 < left_distance <= 130:
                print("Front obstacle detected and left space is between 40 and 75, turning left!")
                turn_degrees("left")
                move_forward(21)  # Move 10 units forward after turning
                continue

        error_left = left_distance - 40
        error_right = right_distance - 40

        print(f"Left Error: {error_left}, Right Error: {error_right}")

        # Apply proportional control for side walls
        left_control = Kp_side * error_left
        right_control = Kp_side * error_right
        print(f"Left Control Adjustment: {left_control}, Right Control Adjustment: {right_control}")

        l_speed = get_saturated_speed(-1*left_control + right_control)
        r_speed = get_saturated_speed(left_control - right_control)

        controller.set_speed_l(l_speed)
        controller.set_speed_r(r_speed)

        print(f"Left Motor Speed: {l_speed}, Right Motor Speed: {r_speed}")

# Test the wall following function
Kp_side = 0.1
wall_following(controller=controller, Kp_side=Kp_side)
