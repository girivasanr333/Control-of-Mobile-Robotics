import time
import robot_controller
import pigpio
import signal

pigpi = pigpio.pi()

controller = robot_controller.control(pi=pigpi)

def SignalHandler_SIGINT(SignalNumber,Frame):
     print('Stopping Controller')
     controller.set_speed_r(0)
     controller.set_speed_l(0)
     exit(0)

#register the signal with Signal handler
signal.signal(signal.SIGINT,SignalHandler_SIGINT)

def move(controller, l_speed, r_speed, D, T, both=True):
        
        number_ticks = D/controller.tick_length()
        
        controller.sampling_time = T
        turns_l = 0
        turns_r = 0

        angle_l = controller.get_angle_l()
        angle_r = controller.get_angle_r()
        
        print("Angle L: " + str(angle_l))
        print("Angle R: " + str(angle_r))

        target_angle_r = controller.get_target_angle(number_ticks = number_ticks, angle = angle_r)
        target_angle_l = controller.get_target_angle(number_ticks = number_ticks, angle = angle_l)
        
        print("Target Angle L: " + str(target_angle_l))
        print("Target Angle R: " + str(target_angle_r))
        

        

        position_reached_l = False
        position_reached_r = False
        reached_sp_counter = 0
        #position must be reached for one second to allow
        #overshoots/oscillations before stopping control loop
        wait_after_reach_sp = 1/controller.sampling_time

        #start time of the control loop
        start_time = time.time()
        # speed = 0.3
        # l_speed = speed
        # r_speed = speed
        
        #control loop:
        while not position_reached_r or not position_reached_l:
            #DEBUGGING OPTION:
            #printing runtime of loop , see end of while true loop
            start_time_each_loop = time.time()

            angle_l = controller.get_angle_l()
            angle_r = controller.get_angle_r()
#             print("Angle L: " + str(angle_l))
#             print("Angle R: " + str(angle_r))

          #  print(controller.imu.gyro)

            angle_diff = angle_l - angle_r

            #try needed, because:
            #- first iteration of the while loop prev_angle_* is missing and the
            #method controller.get_total_angle() will throw an exception.
            #- second iteration of the while loop prev_total_angle_* is missing,
            #which will throw another exception
            try:
                turns_l, total_angle_l = controller.get_total_angle(angle_l, controller.unitsFC, prev_angle_l, turns_l)
                turns_r, total_angle_r = controller.get_total_angle(angle_r, controller.unitsFC, prev_angle_r, turns_r)

                total_angle_diff = round(total_angle_l - (total_angle_r + angle_diff), 2)

                #speed = speed + 0.01
              

                # if (total_angle_diff) == 0:
                #     r_speed = speed
                #     l_speed = speed
                # elif total_angle_diff > 0:
                #     print("left is fast")
                #     print("Total Angle L: " + str(total_angle_l))
                #     print("Total Angle R: " + str(total_angle_r + angle_diff))
                #     r_speed = speed + 0.1
                #     l_speed = speed - 0.15
                      
                # else:
                #     print("right is fast")
                #     print("Total Angle L: " + str(total_angle_l))
                #     print("Total Angle R: " + str(total_angle_r + angle_diff))
                #     l_speed = l_speed + 0.1
                #     r_speed = speed - 0.15
                      
                # l_speed = speed
                # r_speed = speed

                controller.set_speed_r(r_speed)
                controller.set_speed_l(l_speed)

            except Exception:
                pass

            prev_angle_l = angle_l
            prev_angle_r = angle_r

            #try needed, because first iteration of the while loop prev_angle_* is
            #missing and the method controller.get_total_angle() will throw an exception,
            #and therefore no total_angle_* gets calculated

            try:
                prev_total_angle_l = total_angle_l
                prev_total_angle_r = total_angle_r
            except Exception:
                pass

            try:
#                 controller.set_speed_l(0.0)
#                 controller.set_speed_r(0.0)
                reached_sp_counter += 1

#                 if reached_sp_counter >= wait_after_reach_sp:

                if target_angle_r <= total_angle_r:
                    controller.set_speed_r(0.0)
                    position_reached_r = True
                    if not both:
                        position_reached_l = True
                        controller.set_speed_l(0.0)
                    print("R pos reached")
                    print(controller.imu.gyro)
                else:
                    pass
                if target_angle_l <= total_angle_l:
                    controller.set_speed_l(0.0)
                    position_reached_l = True
                    if not both:
                        controller.set_speed_r(0.0)
                        position_reached_r = True
                    print("L pos reached")

                    print(controller.imu.gyro)
                else:
                    pass

            except Exception:
                pass

            #Pause control loop for chosen sample time
            #https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python/25251804#25251804
            time.sleep(controller.sampling_time - ((time.time() - start_time) % controller.sampling_time))

            #DEBUGGING OPTION:
            #printing runtime of loop, see beginning of while true loop
            #print('{:.20f}'.format((time.time() - start_time_each_loop)))
          #  print(controller.imu.gyro)
        
        return None

#function to turn
def turn(direction, d):
    if(direction == "left"):
        move(controller=controller, l_speed=-0.3, r_speed=0.3, D=d, T=0.005, both=False)

    elif(direction == "right"):
        #move(controller=controller, l_speed=0.3, r_speed=0, D=d, T=0.005, both=False)
        move(controller=controller, l_speed=0.3, r_speed=-0.3, D=d, T=0.005, both=False)


  
#function to go straight
def forward(d):
    move(controller=controller, l_speed=0.3, r_speed=0.31, D=d, T=0.005, both=True)


print(controller.imu.gyro)
#move(controller=controller,D= 500,T= 0.005)
time.sleep(0.2)
#move(controller=controller,D= 500,T= 0.005)
print("Foward")
forward(1000)
print("Right")
time.sleep(0.2)
turn("right", 112)
time.sleep(0.2)
forward(1000)
time.sleep(0.2)
turn("left",112) 

print(controller.imu.gyro)


