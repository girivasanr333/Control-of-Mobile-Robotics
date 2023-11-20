import time
import robot_controller
import pigpio

# Initialize the pigpio library
pigpi = pigpio.pi()

# Initialize the robot controller
controller = robot_controller.control(pi=pigpi)

max_speed = 0.40
min_speed = 0.35
normal_speed = 0.3

min_front_speed = 0.0

set_distance = 12 # Set distance from the wall
front_set_distance = 25 #front wall
max_distance = 40 #distance between right & left wall

Kp_side = 0.1  # Replace with the best Kp value from your tests


def get_sensor_reading( threshold_distance=40):
    # Get the primary distance sensor readings
    front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()

    print(f"front distance: {front_distance}, left distance: {left_distance}, right distance: {right_distance}")
    front = "no wall"
    left = "no wall"
    right = "no wall"
    # Check if there's a wall in any of the directions based on the threshold
    if front_distance < threshold_distance:
        front = 'wall'
    if left_distance < threshold_distance:
        left = "wall"
    if right_distance < threshold_distance:
        right = "wall"
    
    return front, left, right



# Define the move function
def move( l_speed = .3, r_speed=.3, D=200, T=0.001, both=False):
    # Calculate the number of ticks needed for the given distance
    number_ticks = D / controller.tick_length()
    # Set the sampling time
    controller.sampling_time = T
    # Initialize variables to keep track of turns and angles
    turns_l = 0
    turns_r = 0
    angle_l = controller.get_angle_l()
    angle_r = controller.get_angle_r()

  

    # Calculate the target angles for the left and right motors
    target_angle_r = controller.get_target_angle(number_ticks=number_ticks, angle=angle_r)
    target_angle_l = controller.get_target_angle(number_ticks=number_ticks, angle=angle_l)


    # Initialize variables for loop control
    position_reached_l = False
    position_reached_r = False
    reached_sp_counter = 0
    wait_after_reach_sp = 1 / controller.sampling_time

    # Capture the start time of the move
    start_time_move = time.time()

    prev_angle_l = angle_l
    prev_angle_r = angle_r

    # Loop until both positions are reached
    while not position_reached_r or not position_reached_l:
        start_time_each_loop = time.time()
        front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()


        # Get the current angles of the left and right motors
        angle_l = controller.get_angle_l()
        angle_r = controller.get_angle_r()
        angle_diff = angle_l - angle_r

        try:
            # Calculate the total angles turned by the left and right motors
            turns_l, total_angle_l = controller.get_total_angle(angle_l, controller.unitsFC, prev_angle_l, turns_l)
            turns_r, total_angle_r = controller.get_total_angle(angle_r, controller.unitsFC, prev_angle_r, turns_r)
            total_angle_diff = round(total_angle_l - (total_angle_r + angle_diff), 2)

            # Set the speed for the left and right motors
            controller.set_speed_r(r_speed)
            controller.set_speed_l(l_speed)

        except Exception:
            pass

        prev_angle_l = angle_l
        prev_angle_r = angle_r

        try:
            reached_sp_counter += 1

            # Check if the right motor has reached the target angle
            if target_angle_r <= total_angle_r:
                controller.set_speed_r(0.0)
                position_reached_r = True
                # Capture the end time and print the time taken for the right motor
                end_time_move = time.time()

                if not both:
                    position_reached_l = True
                    controller.set_speed_l(0.0)
                    
            # Check if the left motor has reached the target angle
            if target_angle_l <= total_angle_l:
                controller.set_speed_l(0.0)
                position_reached_l = True
                # Capture the end time and print the time taken for the left motor
                end_time_move = time.time()

                if not both:
                    position_reached_r = True
                    controller.set_speed_r(0.0)
          
        except Exception:
            pass

    return None

# Function to ensure speed values remain within set bounds.
def get_saturated_speed(speed):
    if(speed > max_speed):
        return max_speed
    elif(speed < min_speed):
        return min_speed
    else:
        return speed
    
# Function to make the robot turn by a specified degree either left or right.
def turn_degrees(direction="right", degrees=90):
    # turn_duration = 0.75 * (degrees/90)
    # if direction == "right":
    #     controller.set_speed_l(0.3)
    #     controller.set_speed_r(-0.3)
    # else:
    #     controller.set_speed_l(-0.3)
    #     controller.set_speed_r(0.3)
    # time.sleep(turn_duration)
    controller.set_speed_l(0)
    controller.set_speed_r(0)
    front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()

    if direction == "right":
        move( .3, -.3, 90, 0.001, False)
    else:
        move( -.3, .3, 90, 0.001, False)


def move_cell ():
    controller.set_speed_l(0)
    controller.set_speed_r(0)
    controller.get_primary_distance_sensor_readings()

    move( .3, .3, 320, 0.001, False)

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

def wall_following(controller, Kp_side=0.1):
    print(f"Starting wall following with Kp_side: {Kp_side}")

    start_time = time.time()
    current_time = start_time
    l_speed = normal_speed
    r_speed = normal_speed

    # Default direction
    direction = "left"

    # Loop until 60 seconds has passed.
    while True:
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
        if(front_distance < front_set_distance):
            l_speed = 0.0
            r_speed = 0.0
            controller.set_speed_l(0)
            controller.set_speed_r(0)
            time.sleep(1)
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
#wall_following(controller=controller, Kp_side=Kp_side)
