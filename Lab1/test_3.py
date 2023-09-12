import time
import robot_controller
import pigpio

# Define the 'move' function
def move(controller, Vl, Vr, D, T):
        
        # Calculate the number of ticks based on the distance and tick length
        number_ticks = D/controller.tick_length()
        
        # Set the sampling time for the control loop
        controller.sampling_time = T
        turns_l = 0
        turns_r = 0
         
        # Get initial angles for the left and right wheels

        angle_l = controller.get_angle_l()
        angle_r = controller.get_angle_r()

        # Calculate target angles for left and right based on number of ticks and current angle

        target_angle_r = controller.get_target_angle(number_ticks = number_ticks, angle = angle_r)
        target_angle_l = controller.get_target_angle(number_ticks = number_ticks, angle = angle_l)

        

        position_reached = False
        reached_sp_counter = 0
        #position must be reached for one second to allow
        #overshoots/oscillations before stopping control loop
        
        # Calculate the number of iterations needed after the setpoint is reached, to ensure stability

        wait_after_reach_sp = 1/controller.sampling_time

        #start time of the control loop
        start_time = time.time()

        #control loop: will run until the desired position is reached
        while not position_reached:
            #DEBUGGING OPTION:
            #printing runtime of loop , see end of while true loop
            start_time_each_loop = time.time()

            # Get current angles for the left and right wheels
            angle_l = controller.get_angle_l()
            angle_r = controller.get_angle_r()

            #try needed, because:
            #- first iteration of the while loop prev_angle_* is missing and the
            #method controller.get_total_angle() will throw an exception.
            #- second iteration of the while loop prev_total_angle_* is missing,
            #which will throw another exception
            try:
                turns_l, total_angle_l = controller.get_total_angle(angle_l, controller.unitsFC, prev_angle_l, turns_l)
                turns_r, total_angle_r = controller.get_total_angle(angle_r, controller.unitsFC, prev_angle_r, turns_r)

                # Set speed for both motors

                controller.set_speed_r(.5)
                controller.set_speed_l(.5)

            except Exception:
                pass
            
            # Store the current angles for the next iteration
            prev_angle_l = angle_l
            prev_angle_r = angle_r

            #try needed, because first iteration of the while loop prev_angle_* is
            #missing and the method controller.get_total_angle() will throw an exception,
            #and therefore no total_angle_* gets calculated

            # Try block to store total angles. 
            # Catches exceptions in case the total angles haven't been calculated yet.
            try:
                prev_total_angle_l = total_angle_l
                prev_total_angle_r = total_angle_r
            except Exception:
                pass

            try:
            
            # Check if target angles have been reached for both motors

                reached_sp_counter += 1

#                 if reached_sp_counter >= wait_after_reach_sp:

                if target_angle_r <= total_angle_r:
                    controller.set_speed_r(0.0)
                    position_reached = True
                else:
                    pass
                if target_angle_l <= total_angle_l:
                    controller.set_speed_l(0.0)
                    position_reached = True
                else:
                    pass

            except Exception:
                pass

            #Pause control loop for chosen sample time
            #https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python/25251804#25251804
            time.sleep(controller.sampling_time - ((time.time() - start_time) % controller.sampling_time))

            #DEBUGGING OPTION:
            #printing runtime of loop, see beginning of while true loop
            print('{:.20f}'.format((time.time() - start_time_each_loop)))
        
        return None

# Initialize the pigpio library
pigpi = pigpio.pi()

 # Initialize the robot controller      
controller = robot_controller.control(pi=pigpi)

# Call the move function to move the robot

move(controller=controller,Vl=5,Vr=5, D= 1000,T= 0.2)

# controller.set_speed_r(0)
# controller.set_speed_l(0)
