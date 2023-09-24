
import time
import robot_controller
import pigpio
from pygame import mixer

# Initialize the pigpio library and define constants for direction
pigpi = pigpio.pi()
left = "left"
right = "right"
straight = "straight"

# Initialize the robot controller
controller = robot_controller.control(pi=pigpi)

# Define the move function
def move(controller, l_speed, r_speed, D, T, both=True):
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

    # Print the target angles of the left and right motors
    print("Target Angle L: " + str(target_angle_l))
    print("Target Angle R: " + str(target_angle_r))

    # Initialize variables for loop control
    position_reached_l = False
    position_reached_r = False
    reached_sp_counter = 0
    wait_after_reach_sp = 1 / controller.sampling_time

    # Capture the start time of the move
    start_time_move = time.time()

    # Print the speed of the left and right motors
    print("Left Motor Speed: ", l_speed)
    print("Right Motor Speed: ", r_speed)

    prev_angle_l = angle_l
    prev_angle_r = angle_r

    # Loop until both positions are reached
    while not position_reached_r or not position_reached_l:
        start_time_each_loop = time.time()

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
                print("Time taken to reach the position: ", end_time_move - start_time_move, " seconds")

                if not both:
                    position_reached_l = True
                    controller.set_speed_l(0.0)
                print("R pos reached")
                print(controller.imu.gyro)
            # Check if the left motor has reached the target angle
            if target_angle_l <= total_angle_l:
                controller.set_speed_l(0.0)
                position_reached_l = True
                # Capture the end time and print the time taken for the left motor
                end_time_move = time.time()
                print("Time taken to reach the position: ", end_time_move - start_time_move, " seconds")

                if not both:
                    position_reached_r = True
                    controller.set_speed_r(0.0)
                print("L pos reached")
                print(controller.imu.gyro)

        except Exception:
            pass

        # Sleep for the remaining time in the sampling period
        time.sleep(controller.sampling_time - ((time.time() - start_time_each_loop) % controller.sampling_time))

    return None

# Define the robot function to turn in a given direction and distance
def robot(direction, d):
    # If the direction is left, turn left
    if(direction == "left"):
        print("\nLeft turn:\n")
        move(controller=controller, l_speed=-0.3, r_speed=0.3, D=d, T=0.005, both=False)

    # If the direction is right, turn right
    elif(direction == "right"):
        print("\nRight turn:\n")
        move(controller=controller, l_speed=0.3, r_speed=-0.3, D=d, T=0.005, both=False)
    
    # If the direction is straight, move straight
    elif(direction == "straight"):
        print("\nForward:\n")
        move(controller=controller, l_speed=0.3, r_speed=0.31, D=d, T=0.005, both=True)
    
    time.sleep(0.2)

# Initialize the pygame mixer and load the music file
mixer.init()
mixer.music.load("movebitch.mp3")
# Play the music file 
mixer.music.play(-1,0.0)

# Print the initial gyro reading from the controller's IMU
print(controller.imu.gyro)

time.sleep(0.2)

# Move the robot along a predefined path with various directions and distances
print("p0->p1")
robot(straight, 430)
robot(straight, 300)
robot(straight, 300)
robot(straight, 450)

print("p1->p2")
robot(left, 105)

print("p2->p3")
robot(straight, 430)
robot(straight, 550)
robot(straight, 430)

print("p3->p4")
robot(left, 105)

print("p5->p6")
robot(straight, 300)

print("p6->p7")
robot(left, 105)

print("p7->p8")
robot(straight, 420)
robot(straight, 420)

print("p8")
robot(right, 105)

print("p8->p9")
robot(straight, 350)

print("p9->10")
robot(right, 105)

print("p10->p11")
robot(straight, 415)
robot(straight, 415)

robot(left, 105)

robot(straight, 400)

robot(left, 105)

robot(straight, 430)
robot(straight, 430)

# Print the final gyro reading from the controller's IMU
print(controller.imu.gyro)
