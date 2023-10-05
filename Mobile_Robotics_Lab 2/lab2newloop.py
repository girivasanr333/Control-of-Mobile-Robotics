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
    turn_duration = 0.75 * (degrees/90)  # Adjust based on robot's turning speed for 90-degree
    if direction == "right":
        controller.set_speed_l(0.3)
        controller.set_speed_r(-0.3)
    else if direction == "left":
        controller.set_speed_l(-0.3)
        controller.set_speed_r(0.3)
    time.sleep(turn_duration)
    controller.set_speed_l(0)
    controller.set_speed_r(0)

def wall_following(controller, Kp_side=0.1):
    """Make the robot follow the wall, make decisions based on sensor readings."""
    print(f"Starting wall following with Kp_side: {Kp_side}")

    set_distance = 20  # Desired distance from the wall

    start_time = time.time()
    current_time = start_time

    while current_time - start_time < 30:
        # Retrieve distance sensor readings
        time.sleep(0.1)
        front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()
        print(f"Front Distance: {front_distance}, Right Distance: {right_distance}, Left Distance: {left_distance}")

        # Decision-making based on sensor readings
        #if this doesn't work, try while loop 
        if front_distance < 35 & (left_distance < right_distance):
                print("Obstacle detected, turning right!")
                turn_degrees("right")
        else if front_distance < 35 & (right_distance < left_distance):
                print("Obstacle detected, turning left!")
                turn_degrees("left")   
        else
            print("Cannot move, turning around")
            controller.set_speed_l(0)
            controller.set_speed_r(0)
            #change to 360 degree turn instead of stopping completely, didn't feel like implementing right now
            
           

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
