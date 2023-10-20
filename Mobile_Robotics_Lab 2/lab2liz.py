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

min_front_speed = 0.1

set_distance = 15 # Set distance from the wall
front_set_distance = 22 #front wall
max_distance = 40 #distance between right & left wall

Kp_side = 0.1  # Replace with the best Kp value from your tests


def get_saturated_speed_front_ds(speed):
    if(speed > max_speed):
        return max_speed
    elif(speed < min_front_speed):
        return min_front_speed
    else:
        return speed

def get_saturated_speed(speed):
    if(speed > max_speed):
        return max_speed
    elif(speed < min_speed):
        return min_speed
    else:
        return speed
    




def wall_follow_front_ds(direction="right", Kp_side=0.1):
    """Turns the robot a certain degrees to the specified direction."""
    print("Inside front wall following " + direction)
    #front_distance = controller.get_distance_reading( controller.front_ds)
    front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
    l_speed = 0
    r_speed = 0
    side_control = 0
   

    while front_distance < max_distance:
        if direction == "right":
            side_control = (right_distance - front_distance) * Kp_side
            l_speed =get_saturated_speed_front_ds(side_control)
            #l_speed = 0.3
            r_speed = get_saturated_speed_front_ds(-1*side_control)
            
        else:
            side_control = (left_distance - front_distance) * Kp_side
            l_speed =get_saturated_speed_front_ds(-1*side_control)
            r_speed = get_saturated_speed_front_ds(side_control)
            #r_speed = 0.3
        controller.set_speed_l(l_speed)
        controller.set_speed_r(r_speed)
        front_distance = controller.get_distance_reading( controller.front_ds)

   
    controller.set_speed_l(0)
    controller.set_speed_r(0)
    print("out of front wall following")

def wall_following(controller, Kp_side=0.1):
    
    distance_reached = False

    start_time = time.time()
    current_time = start_time
   # while not distance_reached:

    l_speed = normal_speed
    r_speed = normal_speed

    direction = "left"

    while True:
    #while not distance_reached:
        # Retrieve distance sensor readings
        #time.sleep(0.1)

        front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
        print(f"Front Distance: {front_distance}, Right Distance: {right_distance}, Left Distance: {left_distance}")
        
        # controller.set_speed_l(l_speed)
        # controller.set_speed_r(r_speed)


    
        #
        print(f"Starting wall following in direction: {direction} with Kp_side: {Kp_side}")

        if direction == "left":
            error = left_distance - set_distance
        # elif direction == "right":
        #     error = right_distance - set_distance
        # else:
        #     error = left_distance - right_distance
        
        print(f"Error: {error}")

        # Apply proportional control for side walls
        side_control = Kp_side * (error)
        print(f"Side Control Adjustment: {side_control}")

    
        if direction == "left":
            #move(controller=controller, l_speed=0.4 - side_control, r_speed=0.4 + side_control,  T=0.005)
            l_speed =get_saturated_speed(-1*side_control)
            r_speed = get_saturated_speed(side_control)
        elif direction == "right":
            #move(controller=controller, l_speed=0.4 - side_control, r_speed=0.4 + side_control,  T=0.005)
            l_speed =get_saturated_speed(side_control)
            r_speed = get_saturated_speed(-1*side_control)
        
        
        # if((left_distance > set_distance)):
        #     wall_follow_front_ds(direction="left", Kp_side=Kp_side)
        # elif((front_distance < front_set_distance)):
        #     wall_follow_front_ds(direction="right", Kp_side=Kp_side)

        controller.set_speed_l(l_speed)
        controller.set_speed_r(r_speed)
        
        current_time = time.time()
        print(f"time: {current_time - start_time}")
        
    controller.set_speed_l(0)
    controller.set_speed_r(0)
        

# Test the wall following function

start_time = time.time()
current_time = time.time()
wall_following(controller=controller, Kp_side=Kp_side)

# while current_time - start_time < 20:
#     print("following")
#     wall_following(controller=controller, Kp_side=Kp_side)
#     time.sleep(2)
#     current_time = time.time()


