import time
import robot_controller
import pigpio


def move(controller, Vl, Vr, D, T):
        
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

        #control loop:
        while not position_reached_r and not position_reached_l:
            #DEBUGGING OPTION:
            #printing runtime of loop , see end of while true loop
            start_time_each_loop = time.time()

            angle_l = controller.get_angle_l()
            angle_r = controller.get_angle_r()
#             print("Angle L: " + str(angle_l))
#             print("Angle R: " + str(angle_r))

            print(controller.imu.gyro)

            #try needed, because:
            #- first iteration of the while loop prev_angle_* is missing and the
            #method controller.get_total_angle() will throw an exception.
            #- second iteration of the while loop prev_total_angle_* is missing,
            #which will throw another exception
            try:
                turns_l, total_angle_l = controller.get_total_angle(angle_l, controller.unitsFC, prev_angle_l, turns_l)
                turns_r, total_angle_r = controller.get_total_angle(angle_r, controller.unitsFC, prev_angle_r, turns_r)

                print("Total Angle L: " + str(total_angle_l))
                print("Total Angle R: " + str(total_angle_r))
                #controller.set_speed_r(1)
                #controller.set_speed_l(0)

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
                else:
                    pass
                if target_angle_l <= total_angle_l:
                    controller.set_speed_l(0.0)
                    position_reached_l = True
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

pigpi = pigpio.pi()
        
controller = robot_controller.control(pi=pigpi)
#placement: 7.1in , 6.5 in
controller.set_speed_r(0.5)
controller.set_speed_l(0.49999)
move(controller=controller,Vl=5,Vr=5, D= 1300,T= 0.2) #p0->p1

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.8)
controller.set_speed_l(0)
move(controller=controller,Vl=5,Vr=5, D=103,T= 0.2) #turn left

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.49999)
move(controller=controller,Vl=5,Vr=5, D= 1150,T= 0.2) #p1->p2

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.8)
controller.set_speed_l(0)
move(controller=controller,Vl=5,Vr=5, D=103,T= 0.2)  #turn left

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.49999)
move(controller=controller,Vl=5,Vr=5, D= 220,T= 0.2)#p2->p3

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.8)
controller.set_speed_l(0)
move(controller=controller,Vl=5,Vr=5, D=103,T= 0.2)  #turn left

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.499999)
move(controller=controller,Vl=5,Vr=5, D= 720,T= 0.2) #p3->p4

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0)
controller.set_speed_l(0.8)
move(controller=controller,Vl=5,Vr=5, D=103,T= 0.2)  #turn right

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.5)
move(controller=controller,Vl=5,Vr=5, D= 230,T= 0.2) #p4->p5

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0)
controller.set_speed_l(0.8)
move(controller=controller,Vl=5,Vr=5, D=104,T= 0.2) 

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.5)
move(controller=controller,Vl=5,Vr=5, D= 720,T= 0.2)  #p5->p6

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.8)
controller.set_speed_l(0)
move(controller=controller,Vl=5,Vr=5, D=104,T= 0.2) 

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.5)
move(controller=controller,Vl=5,Vr=5, D= 500,T= 0.2)

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.8)
controller.set_speed_l(0)
move(controller=controller,Vl=5,Vr=5, D=104,T= 0.2) 

controller.set_speed_l(0)
controller.set_speed_r(0)

controller.set_speed_r(0.5)
controller.set_speed_l(0.499999)
move(controller=controller,Vl=5,Vr=5, D= 800,T= 0.2) 
