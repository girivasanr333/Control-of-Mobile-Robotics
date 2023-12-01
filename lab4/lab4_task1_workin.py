import time
import cv2
import numpy as np
import pigpio
import array
import robot_controller
import dsmove


spin_time = 15*4

# # Initialize the pigpio library and robot controller
# pigpi = pigpio.pi()
# controller = robot_controller.control(pi=pigpi)
controller = dsmove.controller

# Constants
max_speed = 0.40
min_speed = 0.35
normal_speed = 0.3
min_front_speed = 0.0
set_distance = 12
front_set_distance = 25
max_distance = 40

Kp_side = 0.1  # Replace with the best Kp value from your tests
number_of_landmarks = 4  # num of landmarks used for trilateration

total_cells = 16  # Total number of cells in the map
collision_threshold = 25   # collision threshold
visited_cells = set()
start_time = time.time()

r1 = 0.813
r2 = 0.812
r3 = 0.812
r4 = 0.812



def trilateration(landmarks):

    x1,y1,r1=landmarks[0].x, landmarks[0].y, landmarks[0].r
    x2,y2,r2=landmarks[1].x, landmarks[1].y, landmarks[1].r
    x3,y3,r3=landmarks[2].x, landmarks[2].y, landmarks[2].r

    # Calculate the coefficients for the linear equations
    A = -2 * x1 + 2 * x2
    B = -2 * y1 + 2 * y2
    C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    
    D = -2 * x2 + 2 * x3
    E = -2 * y2 + 2 * y3
    F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
    
    # Check for the exception when EA = BD, which can lead to division by zero or parallel lines
    if A*E == B*D:
        raise ValueError("Linear equations are not solvable; EA equals BD,or geometrical inconsistency.")
    
    # Calculate the robot's estimated position (x, y)
    x = (C*E - F*B) / (E*A - B*D)
    y = (C*D - A*F) / (B*D - A*E)

    print(f"Robot's position (x, y): ({x}, {y})")
    
    return x, y




# Example of usage:
# frame = robot.blob.camera.read()
# (x, y), radius = getBlobPositionAndRadius(frame, green_hsv.minH, green_hsv.minS, green_hsv.minV, green_hsv.maxH, green_hsv.maxS, green_hsv.maxV)
# if x is not None and y is not None:
#     print(f'x: {x}, y: {y}, radius: {radius}')
############################################################

def getBlobPositionAndRadius(frame, minH, minS, minV, maxH, maxS, maxV):

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame_hsv, (minH, minS, minV), (maxH, maxS, maxV))
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return (None, None), None, None
    largest_contour = max(contours, key=cv2.contourArea)
    (x, y), radius = cv2.minEnclosingCircle(largest_contour)
    if radius < 30:
        return (None, None), None, None
    output_image = frame.copy() #cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    cv2.circle(output_image, (int(x), int(y)), int(radius), (0, 255, 0), 2)
    output_image = mask
    return (x, y), radius, output_image






class HSV_Values:
    def __init__(self, minH, minS, minV, maxH, maxS, maxV):
        self.minH = minH
        self.minS = minS
        self.minV = minV
        self.maxH = maxH
        self.maxS = maxS
        self.maxV = maxV

green_hsv = HSV_Values(44, 92, 95, 74, 180, 220)
pink_hsv = HSV_Values(159, 124, 115, 240, 255, 255)
blue_hsv = HSV_Values(115, 104, 35, 170, 170, 130)
yellow_hsv = HSV_Values(13, 83, 125, 17, 145, 217)

class Landmark:
     def __init__(self, x, y, r):
         self.x = x
         self.y = y
         self.r = r



def find_landmarks(robot, hsv_values):

    found = False
    while not found:
        blob_in_frame = robot.blob.read()
        print(blob_in_frame)
        if len(blob_in_frame) == 0:
            print("Lost Landmark")
            robot.set_speed_l(.15)
            robot.set_speed_r(-.15)
        else:
            # Assuming blob_in_frame contains blobs detected in the frame
            found = True
            for blob in blob_in_frame:
                print(blob.pt)
                # for hsv_value in hsv_values:
                #     if hsv_value.minH <= blob.h <= hsv_value.maxH and \
                #     hsv_value.minS <= blob.s <= hsv_value.maxS and \
                #     hsv_value.minV <= blob.v <= hsv_value.maxV:
                #         # Blob matches the HSV range for the landmark
                #         print(f"Found {hsv_value} landmark")
                        
                #         # Adjust the robot's movement based on the position of the blob
                #         if blob.pt[0] < 250:
                #             robot.set_speed_l(.15)
                #             robot.set_speed_r(-.15)
                #         elif blob.pt[0] > 390:
                #             robot.set_speed_l(-.15)
                #             robot.set_speed_r(.15)
        
            print("No matching landmarks found")
    return False

# Usage example
hsv_landmarks = [green_hsv, pink_hsv, blue_hsv, yellow_hsv]
# find_landmarks(controller, hsv_landmarks)
# controller.set_speed_l(0)
# controller.set_speed_r(0)

# landmarks = [(0.812, 0.812), (-0.812, 0.812), (-0.812, -0.812), (0.812, -0.812)]  # Landmark positions in meters
# #distances = [0.813, r2 = 0.812, r3= 0.812, r4 = 0.812]  # Distances in mm

# try:
#     estimated_x, estimated_y = trilateration(r1, r2, r3, r4, landmarks)
#     print(f"Estimated Position: X={estimated_x} m, Y={estimated_y} m")
# except ValueError as e:
#     print(e)



def find_landmarks_2():

    x = None
    y = None
    counter = 0
    hsv_landmarks = [green_hsv, pink_hsv, blue_hsv, yellow_hsv]
    landmarks = []
   
    for landmark in hsv_landmarks:
        print(f"min hsv: {landmark.minH}")
        start_time = time.time()
        counter = 0
        current_time = time.time()
        while counter == 0 and current_time - start_time < 12 :
            current_time = time.time()
            frame = controller.blob.camera.read()
            (x, y), r, output_image = getBlobPositionAndRadius(frame, landmark.minH, landmark.minS, landmark.minV, landmark.maxH, landmark.maxS, landmark.maxV)
            if x is not None and y is not None:
                print(f'x: {x}, y: {y}, radius: {r}')
                controller.set_speed_l(0)
                controller.set_speed_r(0)
                counter = counter + 1
                landmarks.append(Landmark(x, y, r))
            else:
                controller.set_speed_l(.15)
                controller.set_speed_r(-.15)
    return landmarks

def detect_landmark(landmarks):
    counter = 0
    l = landmarks
    for landmark in hsv_landmarks:
        #print(f"min hsv: {landmark.minH}")
        
        frame = controller.blob.camera.read()
        (x, y), r, output_image = getBlobPositionAndRadius(frame, landmark.minH, landmark.minS, landmark.minV, landmark.maxH, landmark.maxS, landmark.maxV)
        if x is not None and y is not None:
            #print(f'x: {x}, y: {y}, radius: {r}')
            controller.set_speed_l(0)
            controller.set_speed_r(0)
            counter = counter + 1
            l[landmark.minH] =  Landmark(x, y, r)
            break
        
    return l

    
def main():
    start_time = time.time()
    current_time = time.time()
    while current_time - start_time < 60:
        landmarks = find_landmarks_2()
        if len(landmarks) >= 3:
            trilateration(landmarks=landmarks)
        dsmove.move_cell(wf=False)
        dsmove.turn_degrees("right", 90)
        current_time = time.time()
    controller.set_speed_l(0)
    controller.set_speed_r(0)

def test_turn():
    start_time = time.time()
            
    current_time = time.time()
    while  current_time - start_time < 12:
        controller.set_speed_l(.15)
        controller.set_speed_r(-.15)
        current_time = time.time()

    controller.set_speed_l(0)
    controller.set_speed_r(0)

def find_landmarks_3():
    start_time = time.time()
            
    current_time = time.time()
    landmarks = {}
    l_array = []
   
    while  current_time - start_time < spin_time:
        controller.set_speed_l(.15)
        controller.set_speed_r(-.15)
        if len(landmarks) <= 4:
            landmarks = detect_landmark(landmarks=landmarks)
        #time.sleep(0.1)
        current_time = time.time()

    controller.set_speed_l(0)
    controller.set_speed_r(0)
    for l in landmarks:
        print(f'minH: {l}, x: {landmarks[l].x}, y: {landmarks[l].y}, radius: {landmarks[l].r}')
        l_array.append(landmarks[l])
    return l_array
#find_landmarks_3()


#test_turn()

