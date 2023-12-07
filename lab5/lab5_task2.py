
import time
import numpy as np
import dsmove
#import lab5_util as util
#import prob



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
    ['O', 'O', 'W', 'W'],  # Cell 11
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

shortest_path = []
# Visited cells as a 2D array where True indicates a visited cell and False indicates an unvisited cell.
# Initially, all cells are unvisited, so all values are False.
visited_cells = [
    [" . ",  " . ",  " . ",  " . "],  # Cells 1 to 4
    [" . ",  " . ",  " . ",  " . "],  # Cells 5 to 8
    [" . ",  " . ",  " . ",  " . "],  # Cells 9 to 12
    [" . ",  " . ",  " . ",  " . "]  # Cells 13 to 16
]

height, width = 4, 4
num = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1]

wave_cell = np.array(num).reshape((height, width))


class cell:
    def __init__(self, previous_cell, cell_number, direction, turn_direction):
        self.cell_number = cell_number
        self.direction = direction
        self.turn_direction = turn_direction
        self.previous_cell = previous_cell

def compute_wave_numbers(goal_cell, start_cell, current_direction, maze, wave_number,):
  
    new_wave_number = wave_number + 1
    r,c=get_row_column(goal_cell)
    print(f"New Goal cell: {goal_cell}, start cell: {start_cell}, r: {r}, c:{c}, current_direction: {current_direction}")

    
    if(goal_cell == start_cell ) :
        if(wave_cell[r][c] == 1 or wave_cell[r][c] > new_wave_number):
            wave_cell[r][c] = new_wave_number
        return
   
    if(wave_cell[r][c] > 1):
        return
    #update_cell(r, c)
    
    if(wave_cell[r][c] == 1):
        wave_cell[r][c] = new_wave_number
    
    open_cells = get_next_open_cells(goal_cell, current_direction, maze)
   
    print(wave_cell)

    for x in open_cells:
        print(f"Next cell: {x.cell_number}, current_cell: {x.previous_cell}")
        compute_wave_numbers(x.cell_number,start_cell,x.direction, maze, new_wave_number)
       
    return

def get_next_open_cells(current_cell, current_direction, maze):
    # based on current cell and direction, decide the next cell to go
    # get the cell in the direction of travel
    #   if it is not visited already
    #   else choose the next opening
    #   south should be the last choice
    #return cell number and direction
    
    cell_readings = maze[current_cell - 1]
    

    # 0 is "West"
    # 1 is "North"
    # 2 is "East"
    # 3 is "South"

    r, c = get_row_column(current_cell)
    next_cells = []
    found = False
    
    if(cell_readings[0] == "O"):# and not is_cell_visited(r, c, current_direction, "W"):
        dir = "W"
        turn_dir = get_turn_direction(current_direction, dir)
        n_cell = get_next_cell(current_cell, current_direction, turn_dir)
        next_cell = cell(current_cell, n_cell, dir, turn_dir)
        if(current_cell != n_cell and turn_dir != "reverse"):
            print(f"current cell: {current_cell}, next cell: {n_cell}, dir: {dir}, turn dir: {turn_dir}")
            next_cells.append(next_cell)
        found = True

    if(cell_readings[1] == "O"):# and not is_cell_visited(r, c, current_direction, "N"):
        dir = "N"
        turn_dir = get_turn_direction(current_direction, dir)
        n_cell = get_next_cell(current_cell, current_direction, turn_dir)
        next_cell = cell(current_cell, n_cell, dir, turn_dir)
        if(current_cell != n_cell and turn_dir != "reverse"):
            print(f"current cell: {current_cell}, next cell: {n_cell}, dir: {dir}, turn dir: {turn_dir}")
            next_cells.append(next_cell)        
        found = True
    if(cell_readings[2] == "O"):# and not is_cell_visited(r, c, current_direction, "E"):
        dir = "E"
        turn_dir = get_turn_direction(current_direction, dir)
        n_cell = get_next_cell(current_cell, current_direction, turn_dir)
        next_cell = cell(current_cell, n_cell, dir, turn_dir)
        if(current_cell != n_cell and turn_dir != "reverse"):
            print(f"current cell: {current_cell}, next cell: {n_cell}, dir: {dir}, turn dir: {turn_dir}")
            next_cells.append(next_cell)
        found = True
    if(cell_readings[3] == "O"):# and not is_cell_visited(r, c, current_direction, "S"):
        dir = "S"
        turn_dir = get_turn_direction(current_direction, dir)
        n_cell = get_next_cell(current_cell, current_direction, turn_dir)
        next_cell = cell(current_cell, n_cell, dir, turn_dir)
        if(current_cell != n_cell and turn_dir != "reverse"):
            print(f"current cell: {current_cell}, next cell: {n_cell}, dir: {dir}, turn dir: {turn_dir}")
            next_cells.append(next_cell)
        found = True
    # if found == False:
    #     dir = get_reverse_direction(current_direction)
    #     turn_dir = get_turn_direction(current_direction, dir)
    #     n_cell = get_next_cell(current_cell, current_direction, turn_dir)
    #     next_cell = cell(current_cell, n_cell, dir, turn_dir)
    #     next_cells.append(next_cell)
   
    return next_cells


def get_next_cell(current_cell, current_direction, turn_direction):
    row, column = get_row_column(current_cell)
    d = current_direction
    
    if(turn_direction == "straight"):
        r, c, d = forward(row, column, current_direction)
        
    elif(turn_direction == "left"):
         r, c, d = left(row, column, current_direction)
    elif(turn_direction == "right"):
         r, c, d = right(row, column, current_direction)
    elif(turn_direction == "reverse"):
         r, c, d = backward(row, column, current_direction)

    next_cell = get_cell_number(r, c)
    
    #print(f"Next r: {r}, c: {c}, d: {d}, Next cell: {next_cell}")

    return next_cell

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
    #print(f"Direction: {changed_dir}, turn direction: {turn_direction}")
    return turn_direction

def is_cell_visited(row, column, current_direction, new_direction):
    r = row
    c = column
    d = current_direction

    if(r > 3 or c > 3):
        return True
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
    
   # print(f"Next r: {r}, c: {c}, d: {d}, visited: {cell_visited}")

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
    
    #print(f"Incoming values - row: {r}, col: {c}, direction: {d}")
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

    #print(f"New values - row: {r}, col: {c}, direction: {d}")
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

def get_row_column(cell_number):
    r = int((cell_number - 1)/ 4)
    c = (cell_number - 1) % 4
    return r, c

def get_shortest_next_cell(start_cell, current_direction, maze):

    open_cells = get_next_open_cells(start_cell, current_direction, maze)

    wave_score = 999
    next_cell = None

    for x in open_cells:
        r,c = get_row_column(x.cell_number)
        wave = wave_cell[r][c]
        if(wave < wave_score and wave > 1):
            wave_score = wave
            print(f"Next cell: {x.cell_number}, drive direction: {x.turn_direction}, wave: {wave}")
            next_cell = x

    return next_cell

def drive_shortest_path(goal_cell, start_cell, current_direction, maze):
  
    if(goal_cell == start_cell):
        print("Goal Reached...")
        return
    r,c = get_row_column(start_cell)
    s_cell = start_cell
    curr_dir = current_direction
    shortest_path.append(start_cell)
    while(goal_cell != s_cell):
        next_cell = get_shortest_next_cell(s_cell, curr_dir, maze)
        if(next_cell == None):
            break
        print(f"Next cell: {next_cell.cell_number}, drive direction: {next_cell.turn_direction}")

        shortest_path.append(next_cell.cell_number)
        turn_direction = next_cell.turn_direction
        if turn_direction == "straight":
            r, c, _ = move_forward(r, c, curr_dir)
            print(f"Going straight, next cell, next cell: {get_cell_number(r, c)}")
        elif turn_direction == "left":
            print(f"Going Left, next cell: {get_cell_number(r, c)}")
            r, c, _ = move_left(r, c, curr_dir)
        elif turn_direction == "right":
            print(f"Going right, next cell: {get_cell_number(r, c)}")
            r, c, _ = move_right(r, c, curr_dir)
        else:
            print(f"Going backward, next cell: {get_cell_number(r, c)}")
            r, c, _ = move_backward(r, c, curr_dir)
        s_cell = next_cell.cell_number
        curr_dir = next_cell.direction


#print(get_row_column(16))
start_cell = 16
start_dir = "N"
goal_cell = 11
maze = maze1
compute_wave_numbers(goal_cell, start_cell, start_dir, maze, 1)
print("starting the drive")
drive_shortest_path(goal_cell, start_cell, start_dir, maze)
print("Shortest path:")
print(shortest_path)
