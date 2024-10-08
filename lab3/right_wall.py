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

# Define the move function
def move(controller, l_speed, r_speed, D, T, both=False):
    # Calculate the number of ticks needed for the given distance
    number_ticks = D / controller.tick_length()
    # Set the sampling time
    controller.sampling_time = T
    # Initialize variables to keep track of turns and angles
    turns_l = 0
    turns_r = 0
    angle_l = controller.get_angle_l()
    angle_r = controller.get_angle_r()


    print("Angle L: " + str(angle_l))
    print("Angle R: " + str(angle_r))


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
                #print("Time taken to reach the position: ", end_time_move - start_time_move, " seconds")

                if not both:
                    position_reached_l = True
                    controller.set_speed_l(0.0)
                # print("R pos reached")
                # print(controller.imu.gyro)
            # Check if the left motor has reached the target angle
            if target_angle_l <= total_angle_l:
                controller.set_speed_l(0.0)
                position_reached_l = True
                # Capture the end time and print the time taken for the left motor
                end_time_move = time.time()
               # print("Time taken to reach the position: ", end_time_move - start_time_move, " seconds")

                if not both:
                    position_reached_r = True
                    controller.set_speed_r(0.0)
                #print("L pos reached")
                #print(controller.imu.gyro)

        except Exception:
            pass

        # Sleep for the remaining time in the sampling period
        #time.sleep(controller.sampling_time - ((time.time() - start_time_each_loop) % controller.sampling_time))

    return None

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
    


def wall_follow_front_ds(turn_direction="right", Kp_side=0.1):
    #print("Inside front wall following " + turn_direction)
    #front_distance = controller.get_distance_reading( controller.front_ds)
    front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
    l_speed = 0
    r_speed = 0
    side_control = 0
   
   
    while front_distance < max_distance:
        if turn_direction == "right":
            #side_control = (right_distance - front_distance) * Kp_side
            side_control = (right_distance - front_set_distance) * Kp_side
            l_speed =get_saturated_speed_front_ds(-1*side_control)
            #l_speed = 0.3
            r_speed = get_saturated_speed_front_ds(side_control)
            
        else:
            side_control = (right_distance - front_set_distance) * Kp_side
            r_speed =get_saturated_speed_front_ds(-1*side_control)
            l_speed = get_saturated_speed_front_ds(side_control)
            #r_speed = 0.3
        controller.set_speed_l(l_speed)
        controller.set_speed_r(r_speed)
        front_distance = controller.get_distance_reading( controller.front_ds)

   
    controller.set_speed_l(0)
    controller.set_speed_r(0)
    print("out of front wall following")
    

# U Turn 
def turn(direction="right"):
    if(direction == "right"):
        move(controller, 0.6, 0, 200, T=0.005) #90 degree turn 
        move(controller, 0.3, 0.3, 230, T=0.005)
        right_distance = controller.get_distance_reading( controller.right_ds)

        if(right_distance > max_distance):
            print(f"Right Distance: {right_distance}")
            move(controller, 0.6, 0.0, 200, T=0.005)#200
            move(controller, 0.3, 0.3, 200, T=0.005)
        elif(right_distance > set_distance):
              while right_distance < set_distance:
                right_distance = controller.get_distance_reading( controller.right_ds)
                print(f"Right Distance following the wall: {right_distance}")
                move(controller, 0.2, 0.1, 10, T=0.005)

   
def wall_following(controller, Kp_side=0.1):
    
    distance_reached = False
    goal_reached = False

    start_time = time.time()
    current_time = start_time
   # while not distance_reached:

    l_speed = normal_speed
    r_speed = normal_speed

    direction = "right"

    #while True:
    while not goal_reached:
        # Retrieve distance sensor readings
        #time.sleep(0.1)

        front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
      
        blob_in_frame = controller.blob.read()
        
        if len(blob_in_frame) > 0 :
            print(blob_in_frame[0].pt[0])
            if blob_in_frame[0].pt[0] > 250 and blob_in_frame[0].pt[0] < 350:
                print("Found Goal")
                while True:
                    blob_in_frame = controller.blob.read()
                    if len(blob_in_frame) > 0 :
                        if blob_in_frame[0].size > 450:
                            print("Arrived to Goal")
                            controller.set_speed_l(0)
                            controller.set_speed_r(0)
                            goal_reached = True
                            break
                        else:
                            print("Moving to Goal")
                            controller.set_speed_l(.3)
                            controller.set_speed_r(.3)

        if not goal_reached:

            if direction == "right":
                error = right_distance - set_distance
      
            side_control = Kp_side * (error)
            # print(f"Side Control Adjustment: {side_control}")        
            
            if front_distance < front_set_distance:
                if direction == "left":
                    wall_follow_front_ds(turn_direction="right", Kp_side=Kp_side)
                elif direction == "right":
                    wall_follow_front_ds(turn_direction="left", Kp_side=Kp_side)
            else:
                if direction == "right":
                    if right_distance > max_distance :
                        turn(direction="right")
                        distance_reached = True
                        l_speed = 0.0
                        r_speed = 0.0
                    else:
                        l_speed =get_saturated_speed(side_control)
                        r_speed = get_saturated_speed(-1*side_control)
              
            
            controller.set_speed_l(l_speed)
            controller.set_speed_r(r_speed)
                
            current_time = time.time()
            # print(f"time: {current_time - start_time}")
        
    controller.set_speed_l(0)
    controller.set_speed_r(0)
        

# Test the wall following function

start_time = time.time()
current_time = time.time()
wall_following(controller=controller, Kp_side=Kp_side)


