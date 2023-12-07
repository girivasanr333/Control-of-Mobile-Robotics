
import time
#mport numpy as np
import dsmove
import lab5_util as util
#import prob
import occ_map as occ



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

maze3 = [
    ['W', 'W', 'O', 'W'],  # Cell 1
    ['O', 'W', 'O', 'W'],  # Cell 2
    ['O', 'W', 'O', 'O'],  # Cell 3
    ['O', 'W', 'W', 'O'],  # Cell 4
    ['W', 'W', 'O', 'O'],  # Cell 5
    ['O', 'W', 'W', 'O'],  # Cell 6
    ['W', 'O', 'W', 'O'],  # Cell 7
    ['W', 'O', 'W', 'O'],  # Cell 8
    ['W', 'O', 'W', 'O'],  # Cell 9
    ['W', 'O', 'O', 'W'],  # Cell 10
    ['O', 'Q', 'W', 'W'],  # Cell 11
    ['W', 'O', 'W', 'O'],  # Cell 12
    ['W', 'O', 'O', 'W'],  # Cell 13
    ['O', 'W', 'O', 'W'],  # Cell 14
    ['O', 'W', 'O', 'W'],  # Cell 15
    ['O', 'O', 'W', 'W']   # Cell 16
]

maze_open = [
    ['W', 'W', 'O', 'O'],  # Cell 1
    ['O', 'W', 'O', 'O'],  # Cell 2
    ['O', 'W', 'O', 'O'], # Cell 3
    ['O', 'W', 'W', 'O'],  # Cell 4
    ['W', 'O', 'O', 'O'],  # Cell 5
    ['O', 'O', 'O', 'O'],  # Cell 6
    ['O', 'O', 'O', 'O'],  # Cell 7
    ['O', 'O', 'W', 'O'], # Cell 8
    ['W', 'O', 'O', 'O'],  # Cell 9
    ['O', 'O', 'O', 'O'],  # Cell 10
    ['O', 'O', 'O', 'O'], # Cell 11
    ['O', 'O', 'W', 'O'], # Cell 12
    ['W', 'O', 'O', 'W'],  # Cell 13
    ['O', 'O', 'O', 'W'],  # Cell 14
    ['O', 'O', 'O', 'W'], # Cell 15
    ['O', 'O', 'W', 'W'],  # Cell 16
]


# Visited cells as a 2D array where True indicates a visited cell and False indicates an unvisited cell.
# Initially, all cells are unvisited, so all values are False.
visited_cells = [
    [" . ",  " . ",  " . ",  " . "],  # Cells 1 to 4
    [" . ",  " . ",  " . ",  " . "],  # Cells 5 to 8
    [" . ",  " . ",  " . ",  " . "],  # Cells 9 to 12
    [" . ",  " . ",  " . ",  " . "]  # Cells 13 to 16
]
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

def get_next_direction(row, column, current_cell, current_direction, maze):
    # based on current cell and direction, decide the next cell to go
    # get the cell in the direction of travel
    #   if it is not visited already
    #   else choose the next opening
    #   south should be the last choice
    #return cell number and direction
    
    cell_readings = maze[current_cell - 1]
    print(f"Current Cell in next direction: {row}, Y: {column}, cell number: {current_cell}, cell openings: {cell_readings}")
    

    # 0 is "West"
    # 1 is "North"
    # 2 is "East"
    # 3 is "South"

    r = row
    c = column
    d = current_direction

    direction_index = 0
    if(d == "W" ):
        direction_index = 0
    elif(d =="N"):
        direction_index = 1
    elif(d =="E"):
        direction_index = 2
    elif(d =="S"):
        direction_index = 3
 
   
    if(cell_readings[direction_index] == "O") and not is_cell_visited(row, column, current_direction, current_direction):
        d = current_direction
    elif(cell_readings[0] == "O") and not is_cell_visited(row, column, current_direction, "W"):
        d = "W"
    elif(cell_readings[1] == "O") and not is_cell_visited(row, column, current_direction, "N"):
        d = "N"
    elif(cell_readings[2] == "O") and not is_cell_visited(row, column, current_direction, "E"):
        d = "E"
    elif(cell_readings[3] == "O") and not is_cell_visited(row, column, current_direction, "S"):
        d = "S"
   
    elif(cell_readings[direction_index] == "O"):
        d = current_direction
    else:
        d = get_reverse_direction(current_direction)
    print(f"New direction: {d}")

    return d

def get_reverse_direction(dir):
    reverse_dir = ""
    if (dir == "E"):
        reverse_dir = "W"
    elif(dir == "W"):
        reverse_dir = "E"
    elif(dir == "N"):
        reverse_dir = "S"
    elif(dir == "S"):
        reverse_dir = "N"
    return reverse_dir
    


def get_turn_direction(d, new_d):
    changed_dir = d + new_d
    turn_direction = "straight"
    if(changed_dir in ["NW", "SE", "EN", "WS"]):
        turn_direction = "left"
    elif(changed_dir in ["NE", "SW", "ES", "WN"]):
        turn_direction = "right"
    elif(changed_dir in ["NS", "SN", "EW", "WE"]):
        turn_direction = "reverse"
    elif(changed_dir in ["NN", "SS", "EE", "WW"]):
        turn_direction = "straight"
    print(f"Direction: {changed_dir}, turn direction: {turn_direction}")
    return turn_direction

def is_cell_visited(row, column, current_direction, new_direction):
    r = row
    c = column
    d = current_direction
    cell_visited = False
    turn_direction = get_turn_direction(current_direction, new_direction)
    if(turn_direction == "straight"):
        r, c, d = forward(row, column, current_direction)
        
    elif(turn_direction == "left"):
         r, c, d = left(row, column, current_direction)
    elif(turn_direction == "right"):
         r, c, d = right(row, column, current_direction)
    elif(turn_direction == "reverse"):
         r, c, d = backward(row, column, current_direction)

    
    if visited_cells[r][c] == " . ":
        cell_visited = False
    else:
        cell_visited = True
    
    print(f"Next r: {r}, c: {c}, d: {d}, visited: {cell_visited}")

    return cell_visited
        
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


def print_visited_cells():
    x = '\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in visited_cells])
    print(x)
    #print(visited_cells)


def update_cell(row, column):
    visited_cells[row][column] = " X "
    print(f"Current Cell X: {row}, Y: {column}")



def move_left(r, c, d):
    # dsmove.turn_for_front_ds("left")
    dsmove.turn_degrees("left", 90)

    dsmove.move_cell()
    return left(r, c, d)

def left(row, column, direction):
    r = row
    c = column
    d = direction
    
    print(f"Incoming values - row: {r}, col: {c}, direction: {d}")
    if(direction == "N"):
        d = "W"
        c = c - 1
    if(direction == "E"):
        d = "N"
        r = r - 1
    if(direction == "W"):
        d = "S"
        r = r +1
    if(direction == "S"):
        d = "E"
        c = c + 1

    print(f"New values - row: {r}, col: {c}, direction: {d}")
    return r, c, d

def move_right(r, c, d):
    # dsmove.turn_for_front_ds("right")
    dsmove.turn_degrees("right", 90)

    
    dsmove.move_cell()
    return right(r, c, d)


def right(row, column, direction):
    r = row
    c = column
    d = direction
    
    #dsmove.turn_degrees(90, "right")
    # dsmove.turn_for_front_ds("right")
    
    # dsmove.move_cell()
    if(direction == "N"):
        d = "E"
        c = c + 1
    if(direction == "E"):
        d = "S"
        r = r + 1
    if(direction == "W"):
        d = "N"
        r = r - 1
    if(direction == "S"):
        d = "W"
        c = c - 1

    return r, c, d

def is_next_cell_visited(row, column, direction):
    is_visited = False
    if visited_cells[row][column] == " X ":
        is_visited = True
    return is_visited

def move_forward(r, c, d):
    dsmove.move_cell()
    return forward(r, c, d)


def forward(row, column, direction):

    r = row
    c = column
    d = direction
    # dsmove.move_cell()
    if(direction == "N"):
        r = r - 1
    if(direction == "E"):
        c = c + 1
    if(direction == "W"):
        c = c - 1
    if(direction == "S"):
        r = r + 1

    return r, c, d

def move_backward(r, c, d):
    # dsmove.turn_for_front_ds("right")
    # dsmove.turn_for_front_ds("right")
    dsmove.turn_degrees(90, "right")
    dsmove.turn_degrees(90, "right")
    dsmove.move_cell()
    return backward(r, c, d)


def backward(row, column, direction):

    r = row
    c = column
    d = direction
    # dsmove.move_cell()
    if(direction == "N"):
        r = r + 1
        d="S"
    if(direction == "E"):
        c = c - 1
        d="W"
    if(direction == "W"):
        c = c + 1
        d="E"
    if(direction == "S"):
        r = r - 1
        d="N"

    return r, c, d

def get_cell_number(r, c):
    return r * 4 + c + 1



#dsmove.turn_degrees("left", 90)

def perform_mapping_task_2(controller, maze_number, max_time=180, gridsize=4):

    r = 3
    c = 3
    prev_d = "N"
    d = "N"
    current_cell=16

    start_time = time.time()
   # occupancy_grid = util.initialize_occupancy_grid(grid_cell_size)

    occ.initialize_gridmap()
    occ.initialize_l()
    occ.initialize_p()
    maze = maze1
    if(maze_number == 3):
        maze = maze3

   # while time.time() - start_time < max_time:
    while (time.time()  - start_time) < max_time and not is_all_cells_visited():

        current_cell = get_cell_number(r, c)

        if(maze_number == 1):
            if(gridsize != 4):
                occ.maze1_occupancy_mapping_update(occ.gridmap, current_cell)
            else:
                occ.maze1_occupancy_mapping_update_4x4(occ.gridmap, current_cell)
        elif(maze_number == 3):
                if(gridsize != 4):
                     occ.maze3_occupancy_mapping_update(occ.gridmap, current_cell)
                else:
                    occ.maze3_occupancy_mapping_update_4x4(occ.gridmap, current_cell)
        print(f"Current Cell: {current_cell}" )

        update_cell(r, c)
        print_visited_cells()
        prev_d = d

        d = get_next_direction(r, c, current_cell, prev_d, maze)
        turn_direction = get_turn_direction(prev_d, d)

        if turn_direction == "straight":
           r, c, _ = move_forward(r, c, prev_d)
           print(f"Going straight, next cell, next cell: {get_cell_number(r, c)}")
        elif turn_direction == "left":
           print(f"Going Left, next cell: {get_cell_number(r, c)}")
           r, c, _ = move_left(r, c, prev_d)
        elif turn_direction == "right":
            print(f"Going right, next cell: {get_cell_number(r, c)}")
            r, c, _ = move_right(r, c, prev_d)
        else:
            print(f"Going backward, next cell: {get_cell_number(r, c)}")
            r, c, _ = move_backward(r, c, prev_d)


        #util.update_occupancy_grid(controller, occupancy_grid, grid_cell_size, subcell_size, r*350+350, c*350+350)

        # if util.is_90_percent_mapped(occupancy_grid):
        #     break
        if len(visited_cells) == 16:  # Assuming there are 16 cells
            break


    controller.stop()
    return 


perform_mapping_task_2(dsmove.controller, 1, max_time=180, gridsize=4)


