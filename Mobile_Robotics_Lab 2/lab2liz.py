import time
import robot_controller
import pigpio

# Initializing the pigpio library which is a library to interface with GPIO on a Raspberry Pi.
pigpi = pigpio.pi()

# Initializing our custom robot controller which likely controls motors and reads from sensors.
controller = robot_controller.control(pi=pigpi)

# Defining speed constants.
max_speed = 0.4
min_speed = 0.35
normal_speed = 0.3

# Distance the robot should maintain from walls.
set_distance = 15
front_set_distance = 20
max_distance = 40  # Ideal distance for the robot to decide to make a turn.

# Proportional constant for the PID controller.
Kp_side = 0.1

# Function to ensure speed values remain within set bounds.
def get_saturated_speed(speed):
    if(speed > max_speed):
        return max_speed
    elif(speed < min_speed):
        return min_speed
    else:
        return speed
    

# Function to make the robot turn until there's no obstacle in the front.
def turn_for_front_ds(direction="right"):
    front_distance = controller.get_distance_reading(controller.front_ds)

    while front_distance < max_distance:
        if direction == "right":
            controller.set_speed_l(0.3)
            controller.set_speed_r(-0.3)
        else:
            controller.set_speed_l(-0.3)
            controller.set_speed_r(0.3)
        front_distance = controller.get_distance_reading(controller.front_ds)

    controller.set_speed_l(0)
    controller.set_speed_r(0)

# Main function for wall following.
def wall_following(controller, Kp_side=0.1):
    print(f"Starting wall following with Kp_side: {Kp_side}")

    start_time = time.time()
    current_time = start_time
    l_speed = normal_speed
    r_speed = normal_speed

    # Default direction
    direction = "left"

    # Loop until 60 seconds has passed.
    while current_time - start_time < 60:
        # Give the robot a bit of a break between actions.
        time.sleep(0.1)
        front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()

        # Determine if robot should prioritize the left or right wall.
        if(right_distance < left_distance):
            direction = "right"
        else:
            direction = "left"

        # Proportional control to adjust speed based on how far robot is from the wall.
        if direction == "left":
            error = left_distance - set_distance
        elif direction == "right":
            error = right_distance - set_distance

        side_control = Kp_side * error

        # Adjust robot's speed based on error.
        if direction == "left":
            l_speed = get_saturated_speed(-1*side_control)
            r_speed = get_saturated_speed(side_control)
        elif direction == "right":
            l_speed = get_saturated_speed(side_control)
            r_speed = get_saturated_speed(-1*side_control)
        
        # If there's an obstacle in the front, decide to turn left or right or make a U-turn.
        while(front_distance < front_set_distance):
            '''l_speed = 0.0
            r_speed = 0.0
            controller.set_speed_l(0)
            controller.set_speed_r(0)
            time.sleep(1)'''
            if(right_distance > max_distance):
                turn_for_front_ds("right")
            elif(left_distance > max_distance):
                turn_for_front_ds("left")
            else:
                turn_for_front_ds("right")

        # Set the calculated speeds for left and right motors.
        controller.set_speed_l(l_speed)
        controller.set_speed_r(r_speed)
        
        current_time = time.time()
        
    # Stop the motors after the loop finishes.
    controller.set_speed_l(0)
    controller.set_speed_r(0)
        

# Test the wall following function.
start_time = time.time()
current_time = time.time()
wall_following(controller=controller, Kp_side=Kp_side)

