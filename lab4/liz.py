import time
import robot_controller
import pigpio 
import dsmove

# Initialize the pigpio library and robot controller
pigpi = pigpio.pi()
controller = robot_controller.control(pi=pigpi)

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
landmarks_positions = [(0.812, 0.812), (-0.812, 0.812), (-0.812, -0.812), (0.812, -0.812)]  

total_cells = 16  # Total number of cells in the map
collision_threshold =    # collision threshold
visited_cells = set()
start_time = time.time()



# trilateration
def trilateration(distances, landmarks):
    # Landmark coordinates (converted from mm to meters for consistency)
    x1, y1 = landmarks[0][0] / 1000.0, landmarks[0][1] / 1000.0
    x2, y2 = landmarks[1][0] / 1000.0, landmarks[1][1] / 1000.0
    x3, y3 = landmarks[2][0] / 1000.0, landmarks[2][1] / 1000.0


    
    # Distances to the landmarks (converted from mm to meters for consistency)
    r1 = distances[0] / 1000.0
    r2 = distances[1] / 1000.0
    r3 = distances[2] / 1000.0

    

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
    
    return x, y

landmarks = [(0.812, 0.812), (-0.812, 0.812), (-0.812, -0.812), (0.812, -0.812)]  # Landmark positions in meters
distances = [0.813, r2 = 0.812, r3= 0.812, r4 = 0.812]  # Distances in mm 

try:
    estimated_x, estimated_y = trilateration(distances, landmarks)
    print(f"Estimated Position: X={estimated_x} m, Y={estimated_y} m")
except ValueError as e:
    print(e)



# Function to check if the robot has entered a new cell based on its position
def has_entered_new_cell(current_position, cell_positions):
    

 cell_positions = {
    1: (-0.600, 0.600),
    2: (-0.200, 0.600),
    3: (0.200, 0.600),
    4: (0.600, 0.600),
    5: (-0.600, 0.200),
    6: (-0.200, 0.200),
    7: (0.200, 0.200),
    8: (0.600, 0.200),
    9: (-0.600, -0.200),
    10: (-0.200, -0.200),
    11: (0.200, -0.200),
    12: (0.600, -0.200),
    13: (-0.600, -0.600),
    14: (-0.200, -0.600),
    15: (0.200, -0.600),
    16: (0.600, -0.600)
}

# Set the current target cell index
current_target_index = 0
visited_cells = set()


# Main control loop
while current_target_index < len(cell_positions) and time.time() - start_time < 180:
    # Get the current position of the robot using trilateration
    current_position = get_current_position()
    
    # Check if the robot has entered a new cell
    if has_entered_new_cell(current_position, cell_positions):

        # Add the cell to the visited set
        visited_cells.add(current_target_index + 1)
        
        # Print the estimated pose
        print(f"Entered cell {current_target_index + 1}: {current_position}")
        
        # Increment the target cell index  
        current_target_index += 1
    
    # If there are more cells to visit, move towards the next target cell
    if current_target_index < len(cell_positions):
        target_position = cell_positions[current_target_index]
        move_to_position(*target_position)

# After the loop, check if all cells were visited or if the task ended due to the time limit
if len(visited_cells) == len(cell_positions):
    print("All cells have been navigated.")
else:
    print(f"Task ended after 3 minutes. Cells navigated: {visited_cells}")



class HSV_Values:
    def __init__(self, minH, minS, minV, maxH, maxS, maxV):
        controller.minH = minH
        controller.minS = minS
        controller.minV = minV
        controller.maxH = maxH
        controller.maxS = maxS
        controller.maxV = maxV

green_hsv = HSV_Values(44, 92, 95, 74, 180, 220)
pink_hsv = HSV_Values(159, 124, 115, 240, 255, 255)
blue_hsv = HSV_Values(115, 104, 35, 170, 170, 130)
yellow_hsv = HSV_Values(13, 83, 125, 17, 145, 217)


def find_landmarks(robot, hsv_values):

    blob_in_frame = robot.blob.read()
    print(blob_in_frame)  
    if len(blob_in_frame) == 0:
        print("Lost Landmark")
        robot.set_speed_l(.25)
        robot.set_speed_r(-.25)
    else:
        # Assuming blob_in_frame contains blobs detected in the frame
        for blob in blob_in_frame:
            for hsv_value in hsv_values:
                if hsv_value.minH <= blob.h <= hsv_value.maxH and \
                   hsv_value.minS <= blob.s <= hsv_value.maxS and \
                   hsv_value.minV <= blob.v <= hsv_value.maxV:
                    # Blob matches the HSV range for the landmark
                    print(f"Found {hsv_value} landmark")
                    
                    # Adjust the robot's movement based on the position of the blob
                    if blob.pt[0] < 250:
                        robot.set_speed_l(.15)
                        robot.set_speed_r(-.15)
                    elif blob.pt[0] > 390:
                        robot.set_speed_l(-.15)
                        robot.set_speed_r(.15)
    
        print("No matching landmarks found")
    return False

# Usage example
hsv_landmarks = [green_hsv, pink_hsv, blue_hsv, yellow_hsv]
while not find_landmarks(robot, hsv_landmarks):
    pass

def main():
    while time.time() < time.time()*180:
        dsmove.turn_degrees("right", 90)
        dsmove.move_cell()
        dsmove.turn_degrees("left", 90)
        for i in range(3):
            while time.time() < time.time()*60:
                try:
                    estimated_x, estimated_y = trilateration(distances, landmarks)
                    print(f"Estimated Position: X={estimated_x} m, Y={estimated_y} m")
                except ValueError as e:
                    print(e)

            

