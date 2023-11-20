import time
#mport numpy as np
import pigpio
import robot_controller
import dsmove



# Write an 2d array for visted cell and maze confige

# print visted cells
# update visted cells with cell inpute
# print track of X and Y coordinates and current cell values

# Maze configuration as a 2D array (Matrix) where 'W' is wall, 'O' is no wall.

# The order of walls is WNES (West, North, East, South).
maze1 = [
    ['W', 'W', 'O', 'O'],  # Cell 1
    ['O', 'W', 'O', 'W'],  # Cell 2
    ['O', 'W', 'O', 'W'],  # Cell 3
    ['O', 'W', 'W', 'O'],  # Cell 4
    ['W', 'O', 'O', 'W'],  # Cell 5
    ['O', 'W', 'O', 'W'],  # Cell 6
    ['O', 'W', 'W', 'O'],  # Cell 7
    ['W', 'O', 'O', 'O'],  # Cell 8
    ['W', 'W', 'O', 'O'],  # Cell 9
    ['O', 'W', 'O', 'W'],  # Cell 10
    ['O', 'Q', 'W', 'W'],  # Cell 11
    ['W', 'O', 'W', 'O'],  # Cell 12
    ['W', 'O', 'O', 'W'],  # Cell 13
    ['O', 'W', 'O', 'W'],  # Cell 14
    ['O', 'W', 'O', 'W'],  # Cell 15
    ['O', 'O', 'W', 'W']   # Cell 16
]

# Visited cells as a 2D array where True indicates a visited cell and False indicates an unvisited cell.
# Initially, all cells are unvisited, so all values are False.
visited_cells = [
    [" . ",  " . ",  " . ",  " . "],  # Cells 1 to 4
    [" . ",  " . ",  " . ",  " . "],  # Cells 5 to 8
    [" . ",  " . ",  " . ",  " . "],  # Cells 9 to 12
    [" . ",  " . ",  " . ",  " . "]  # Cells 13 to 16
]

def is_all_cells_visited():
    all_visited = True
    for i in range(0, 4):
        if(not all_visited):
            break
        for j in range(0,4):
            if visited_cells[i][j] == " . ":
                all_visited = False
                break
    return all_visited

def determine_cell_number(x, y, grid_cell_size):
    # Assuming the grid origin (0,0) is at the top-left corner of the grid
    # and the cells are numbered from 1 to 16

    # Calculate the row and column based on x and y
    # Floor division is used to find the index in the grid
    # Adding 1 to convert from 0-indexed to 1-indexed
    col = int(x // grid_cell_size) + 1
    row = int(y // grid_cell_size) + 1

    # Calculate the cell number
    # Since the grid is 4x4, each row adds 4 to the cell number
    cell_number = (row - 1) * 4 + col

    return cell_number


def print_visited_cells():
    x = '\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in visited_cells])
    print(x)
    #print(visited_cells)


def update_cell(row, column):
    visited_cells[row][column] = " X "
    print(f"Current Cell X: {row}, Y: {column}")


def update_state_probabilities(state_probabilities, x, y, nq):
    # Sensor model probabilities
    p_z1_s1 = 0.9  # P(sensor='wall' | state='wall')
    p_z0_s1 = 0.1  # P(sensor='no wall' | state='wall')
    p_z0_s0 = 0.7  # P(sensor='no wall' | state='no wall')
    p_z1_s0 = 0.3 # P(sensor='wall' | state='no wall')

    # Read sensor data to determine if there's a wall or not
    front, left, right = dsmove.get_sensor_reading()

    # Determine if the current sensor reading is 'wall' or 'no wall'
    if front == 'wall':
        z = 1
    else:
        z = 0

    # Calculate the updated probabilities based on Bayes' theorem
    if z == 1:  # If sensor reads 'wall'
        p_s1_given_z1 = (p_z1_s1 * state_probabilities.get(nq, {}).get('s1', 0.5)) / \
                        (p_z1_s1 * state_probabilities.get(nq, {}).get('s1', 0.5) + p_z1_s0 * state_probabilities.get(nq, {}).get('s0', 0.5))
        state_probabilities[nq] = {'s1': p_s1_given_z1, 's0': 1 - p_s1_given_z1}
    else:  # If sensor reads 'no wall'
        p_s0_given_z0 = (p_z0_s0 * state_probabilities.get(nq, {}).get('s0', 0.5)) / \
                        (p_z0_s0 * state_probabilities.get(nq, {}).get('s0', 0.5) + p_z0_s1 * state_probabilities.get(nq, {}).get('s1', 0.5))
        state_probabilities[nq] = {'s0': p_s0_given_z0, 's1': 1 - p_s0_given_z0}



def move_left(row, column, direction):

    r = row
    c = column
    d = direction
    dsmove.turn_degrees(90, "left")
    dsmove.move_cell()
    if(direction == "N"):
        d = "E"
        c = c - 1
    if(direction == "E"):
        d = "S"
        r = r + 1
    if(direction == "W"):
        d = "N"
        r = r - 1
    if(direction == "S"):
        d = "W"
        c = c + 1

    return r, c, d

def move_right(row, column, direction):

    r = row
    c = column
    d = direction
    dsmove.turn_degrees(90, "right")
    dsmove.move_cell()
    if(direction == "N"):
        d = "W"
        c = c + 1
    if(direction == "E"):
        d = "N"
        r = r - 1
    if(direction == "W"):
        d = "S"
        r = r + 1
    if(direction == "S"):
        d = "E"
        c = c - 1

    return r, c, d

def move_forward(row, column, direction):

    r = row
    c = column
    d = direction
    dsmove.move_cell()
    if(direction == "N"):
        r = r - 1
    if(direction == "E"):
        c = c - 1
    if(direction == "W"):
        c = c + 1
    if(direction == "S"):
        r = r + 1

    return r, c, d



def localization( max_time=60):
    # Initialization
    start_time = time.time()
    current_time = start_time
    visited_cells = set()
    current_cell = None
    state_probabilities = {}  # Probabilities for each cell

    

    print("starting..." )
    

    #assumption - starting at position 16 facing north (4,4) cell 16
    r = 3
    c = 3
    d = "N"
    nq=16

    while current_time - start_time < max_time and not is_all_cells_visited():

        front, left, right = dsmove.get_sensor_reading()
        update_cell(r, c)
        print_visited_cells()

   
   # for i in range(columns, 0, -1):
   #  for j in range(rows, 0, -1):
        # Perform an action move
        front, left, right = dsmove.get_sensor_reading()

        if front == "no wall":
            r, c, d = move_forward(r, c, d)
        elif left == "no wall":
            r, c, d = move_left(r, c, d)
        elif right == "no wall":
            r, c, d = move_right(r, c, d)
        else:
            r, c, d = move_right(r, c, d)
            r, c, d = move_right(r, c, d)
        front, left, right = dsmove.get_sensor_reading()
        
        # print(f"Estimated Position: X={estimated_x} m, Y={estimated_y} m")
        print(f"Current sensor: {front}, {left}, {right}")
        

        # Update the current cell based on movement and sensor data
        #x, y, nq = update_current_state(controller)
        #current_cell = nq  # Assuming nq represents the cell number

       
        # Update state probabilities
        update_state_probabilities(state_probabilities, r, r, nq)

        # Print the current state and probability
        print(f"Current state: {r}, {c}, {nq}")
        print(f"State probability: {state_probabilities.get(nq, 0)}")

        current_time = time.time()

        # Check if all cells have been visited
        if len(visited_cells) == 16:  # Assuming there are 16 cells
            break
localization(180)

