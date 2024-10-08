
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

    # Print the initial angles of the left and right motors
    print("Angle L: " + str(angle_l))
    print("Angle R: " + str(angle_r))

    # Calculate the target angles for the left and right motors
    target_angle_r = controller.get_target_angle(number_ticks=number_ticks, angle=angle_r)
    target_angle_l = controller.get_target_angle(number_ticks=number_ticks, angle=angle_l)


    # Initialize variables for loop control
    position_reached_l = False
    position_reached_r = False
    reached_sp_counter = 0
    wait_after_reach_sp = 0 #1 / controller.sampling_time

    # Capture the start time of the move
    start_time_move = time.time()

    prev_angle_l = angle_l
    prev_angle_r = angle_r

    # Loop until both positions are reached
    while not position_reached_r or not position_reached_l:
        start_time_each_loop = time.time()
        front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
        blob_in_frame = controller.blob.read()


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

    front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
    l_speed = 0
    r_speed = 0
    side_control = 0
   
   
    while front_distance < max_distance:
        if turn_direction == "right":
            #side_control = (right_distance - front_distance) * Kp_side
            side_control = (left_distance - front_set_distance) * Kp_side
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
   

def complete_turn(direction="left"):
    left_distance = controller.get_distance_reading( controller.left_ds)

    if(left_distance > max_distance):
        print(f"Left Distance: {left_distance}")
        move(controller, 0.0, 0.6, 200, T=0.005)#200
        move(controller, 0.3, 0.3, 200, T=0.005)
    elif(left_distance > set_distance):
            while left_distance < set_distance:
            left_distance = controller.get_distance_reading( controller.left_ds)
            print(f"Left Distance following the wall: {left_distance}")
            move(controller, 0.1, 0.2, 10, T=0.005)



# U Turn
def turn(direction="left"):
    if(direction == "left"):
        move(controller, 0.0, 0.6, 200, T=0.005) #Turn 90 degrees
        move(controller, 0.3, 0.3, 230, T=0.005)
        # left_distance = controller.get_distance_reading( controller.left_ds)

        # if(left_distance > max_distance):
        #     print(f"Left Distance: {left_distance}")
        #     move(controller, 0.0, 0.6, 200, T=0.005)#200
        #     move(controller, 0.3, 0.3, 200, T=0.005)
        # elif(left_distance > set_distance):
        #       while left_distance < set_distance:
        #         left_distance = controller.get_distance_reading( controller.left_ds)
        #         print(f"Left Distance following the wall: {left_distance}")
        #         move(controller, 0.1, 0.2, 10, T=0.005)

def goal_detected(robot):

    goal_detected = False

    counts_360 = 650
    counts = 0

    # blob_in_frame = controller.blob.read()
    # while not goal_detected:
    #     blob_in_frame = controller.blob.read()
    #     if len(blob_in_frame) > 0 and  blob_in_frame[0].pt[0] > 250 and blob_in_frame[0].pt[0] < 390:
    #         print(blob_in_frame[0].pt[0])
    #         goal_detected = True
    #     else:
    #         if len(blob_in_frame) > 0:
    #             print("Not matching goal")
    #             print(blob_in_frame[0].pt[0])
    #         move(controller, -0.15, 0.15, 2, T=0.000, both=False)
    #         counts = counts + 2

    # move(controller, 0.3, -0.3, 2, T=0.005)

    start_time = time.time()
    current_time = time.time()
    while  not goal_detected and current_time - start_time <5:
        blob_in_frame = robot.blob.read()
        
        if len(blob_in_frame) == 0 :
            print("Lost Landmark")
            robot.set_speed_l(.25)
            robot.set_speed_r(-.25)
        else:
            print(blob_in_frame[0].pt[0])
            if blob_in_frame[0].pt[0] < 250 :
                robot.set_speed_l(.15)
                robot.set_speed_r(-.15)
                #move(controller, -0.15, 0.15, 2, T=0.000, both=False)
                counts = counts + 2
            elif blob_in_frame[0].pt[0] > 390:
                robot.set_speed_l(-.15)
                robot.set_speed_r(.15)
                #move(controller, 0.15, -0.15, 2, T=0.000, both=False)
                counts = counts + 2
            else:
                print("Found Goal")
                goal_detected = True
                # if blob_in_frame[0].size > 450:
                #     print("Arrived to Goal")
                #     robot.set_speed_l(0)
                #     robot.set_speed_r(0)
                #     goal_detected = True
                #     #break
                # else:
                #     print("Moving to Goal")
                #     robot.set_speed_l(.5)
                #     robot.set_speed_r(.5)
        current_time = time.time()
    return goal_detected

   
def wall_following(controller, Kp_side=0.1):
    
    distance_reached = False
    goal_reached = False

    start_time = time.time()
    current_time = start_time
   # while not distance_reached:

    l_speed = normal_speed
    r_speed = normal_speed

    direction = "left"

    goal_det = False


  # Move towards the goal and stop once the goal is reached
  
    #while True:
    while not goal_reached:
        # Retrieve distance sensor readings
        front_distance, right_distance, rear_distance, left_distance = controller.get_primary_distance_sensor_readings()
        
        blob_in_frame = controller.blob.read()
        
        # if len(blob_in_frame) > 0 :
        #     print(blob_in_frame[0].pt[0])
        #     if blob_in_frame[0].pt[0] > 250 and blob_in_frame[0].pt[0] < 350:
        #         print("Found Goal")
        #         while True:
        #             blob_in_frame = controller.blob.read()
                    
        #             if blob_in_frame[0].size > 450:
        #                 print("Arrived to Goal")
        #                 controller.set_speed_l(0)
        #                 controller.set_speed_r(0)
        #                 goal_reached = True
        #                 break
        #             else:
        #                 print("Moving to Goal")
        #                 controller.set_speed_l(.3)
        #                 controller.set_speed_r(.3)


        if goal_det:
            
            
            while not goal_reached:
                blob_in_frame = controller.blob.read()

                print(f"Front Distance: {front_distance}")
                
                if (len(blob_in_frame) > 0 and blob_in_frame[0].size > 450):
                    #print("Arrived to Goal")
                    controller.set_speed_l(0)
                    controller.set_speed_r(0)
                    goal_reached = True
                    break
                elif front_distance < front_set_distance:
                    break
                else:
                    #print("Moving to Goal")
                    controller.set_speed_l(.3)
                    controller.set_speed_r(.3)


        if not goal_reached:

            if direction == "left":
                error = left_distance - set_distance
         
            # Apply proportional control for side walls
            side_control = Kp_side * (error)
           
            
            if front_distance < front_set_distance:
                if direction == "left":
                    wall_follow_front_ds(turn_direction="right", Kp_side=Kp_side)
                elif direction == "right":
                    wall_follow_front_ds(turn_direction="left", Kp_side=Kp_side)
            else:
                if direction == "left":
                    if left_distance > max_distance :
                        turn(direction="left")
                        goal_det = goal_detected(controller)
                        if not complete_turn:
                            complete_turn("left")
                        #goal_reached = True #testing
                        l_speed = 0.0
                        r_speed = 0.0
                    else:
                        l_speed =get_saturated_speed(-1*side_control)
                        r_speed = get_saturated_speed(side_control)
           
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





