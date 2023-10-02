import time
import robot_controller
import pigpio

# Initialize the pigpio library
pigpi = pigpio.pi()

# Initialize the robot controller
controller = robot_controller.control(pi=pigpi)

def move(controller, l_speed, r_speed, D, T):
    """Move the robot with specified speeds for left and right wheels and a given distance."""
    print(f"Moving with l_speed: {l_speed}, r_speed: {r_speed}, Distance: {D}, Time: {T}")
    number_ticks = D / controller.tick_length()
    controller.sampling_time = T
    angle_l = controller.get_angle_l()
    angle_r = controller.get_angle_r()
    target_angle_r = controller.get_target_angle(number_ticks=number_ticks, angle=angle_r)
    target_angle_l = controller.get_target_angle(number_ticks=number_ticks, angle=angle_l)
    position_reached_l = False
    position_reached_r = False
    while not position_reached_r or not position_reached_l:
        angle_l = controller.get_angle_l()
        angle_r = controller.get_angle_r()
        controller.set_speed_r(r_speed)
        controller.set_speed_l(l_speed)
        if target_angle_r <= angle_r:
            controller.set_speed_r(0.0)
            position_reached_r = True
        if target_angle_l <= angle_l:
            controller.set_speed_l(0.0)
            position_reached_l = True
        time.sleep(T)
    return None

def wall_following(controller, direction="left", Kp_side=0.1):
    """Make the robot follow a wall, either on the left or right side."""
    print(f"Starting wall following in direction: {direction} with Kp_side: {Kp_side}")
    if direction not in ["left", "right"]:
        raise ValueError("Direction should be either 'left' or 'right'")
    
    set_distance = 5  # Set distance from the wall

    while True:
        # Retrieve distance sensor readings
        front_distance, right_distance, _, left_distance = controller.get_primary_distance_sensor_readings()
        print(f"Front Distance: {front_distance}, Right Distance: {right_distance}, Left Distance: {left_distance}")
        
        if direction == "left":
            error = left_distance - set_distance
        else:
            error = right_distance - set_distance
        
        print(f"Error: {error}")

        # Apply proportional control for side walls
        side_control = Kp_side * error
        print(f"Side Control Adjustment: {side_control}")
        
        if direction == "left":
            move(controller=controller, l_speed=0.4 - side_control, r_speed=0.4 + side_control, D=0.02, T=0.005)
        else:
            move(controller=controller, l_speed=0.4 + side_control, r_speed=0.4 - side_control, D=0.02, T=0.005)
        
        # Check for 90-degree turn conditions
        if (direction == "left" and left_distance > set_distance*1.5) or (front_distance < set_distance):
            print("Making a 90-degree left turn.")
            move(controller=controller, l_speed=-0.3, r_speed=0.3, D=0.15, T=0.005)
        elif (direction == "right" and right_distance > set_distance*1.5) or (front_distance < set_distance):
            print("Making a 90-degree right turn.")
            move(controller=controller, l_speed=0.3, r_speed=-0.3, D=0.15, T=0.005)
        
        # Check for 180-degree turn conditions
        if left_distance < set_distance and right_distance < set_distance:
            print("Blocked from both sides. Making a 180-degree turn.")
            move(controller=controller, l_speed=-0.3, r_speed=0.3, D=0.3, T=0.005)

# Test the wall following function
Kp_side = 0.1  # Replace with the best Kp value from your tests
wall_following(controller=controller, direction="left", Kp_side=Kp_side)
