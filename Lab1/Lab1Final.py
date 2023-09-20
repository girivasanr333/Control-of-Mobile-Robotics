import time
import robot_controller
import pigpio
import signal
from pygame import mixer

pigpi = pigpio.pi()
left = "left"
right = "right"
straight = "straight"

controller = robot_controller.control(pi=pigpi)

'''def SignalHandler_SIGINT(SignalNumber,Frame):
     print('Stopping Controller')
     controller.set_speed_r(0)
     controller.set_speed_l(0)
     exit(0)
'''
#register the signal with Signal handler
#signal.signal(signal.SIGINT,SignalHandler_SIGINT)

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
def robot(direction, d):
    if(direction == "left"):
        print("\nLeft turn:\n")
        move(controller=controller, l_speed=-0.3, r_speed=0.3, D=d, T=0.005, both=False)

    elif(direction == "right"):
        #move(controller=controller, l_speed=0.3, r_speed=0, D=d, T=0.005, both=False)
        print("\nRight turn:\n")
        move(controller=controller, l_speed=0.3, r_speed=-0.3, D=d, T=0.005, both=False)
    
    elif(direction == "straight"):
        print("\nForward:\n")
        move(controller=controller, l_speed=0.3, r_speed=0.31, D=d, T=0.005, both=True)
    
    time.sleep(0.2)


mixer.init()
mixer.music.load("movebitch.mp3")
mixer.music.play(-1,0.0)


print(controller.imu.gyro)

time.sleep(0.2)
 
#move in intervals of <600 for accuracy

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

print(controller.imu.gyro)


