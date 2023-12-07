
import time
#mport numpy as np

import robot_controller
#import lab4_task2 as t2

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



def initialize_occupancy_grid(grid_cell_size, subcell_size):
    # Determine the number of subcells in each dimension
    num_subcells_per_cell = grid_cell_size // subcell_size
    total_subcells = 20 #num_subcells_per_cell ** 2

    # Initialize the occupancy grid with 0.5 (unknown) for each subcell
    occupancy_grid = [[0.5 for _ in range(total_subcells)] for _ in range(total_subcells)]
    return occupancy_grid


def update_occupancy_grid(controller, occupancy_grid, r, c):
    # Get the robot's current position and sensor readings
   # x, y = controller.get_position()
    distance_to_wall = controller.get_distance_reading(controller.front_ds)
    print(f"distance to wall: {distance_to_wall}")
    #distance_to_wall, _, _, _ = controller.get_primary_distance_sensor_readings()


    # Calculate the grid and subcell indices
   # grid_x, grid_y = int(x // grid_cell_size), int(y // grid_cell_size)
    
    #subcell_x, subcell_y = grid_x * 4 + int(x % grid_cell_size  // subcell_size), grid_y * 4 + int(y % grid_cell_size // subcell_size)

    subcell_x, subcell_y = r*4 + 3, c*4 + 3
    #print(f"grid x:  {grid_x}, grid y: {grid_y} ")
    print(f"subcell_x:  {subcell_x}, subcell_y: {subcell_y} ")
    # Update occupancy values
    # 0.3 for empty cells, 0.6 for walls, retain 0.5 for unknown
    if distance_to_wall < 40:
        # Update nearby subcells as empty
        occupancy_grid[subcell_x][subcell_y] = 0.3
    else:
        # Update the corresponding subcell as a wall
        occupancy_grid[subcell_x][subcell_y] = 0.6
    return occupancy_grid

def is_90_percent_mapped(occupancy_grid):
    total_subcells = len(occupancy_grid) ** 2
    mapped_subcells = sum(subcell != 0.5 for row in occupancy_grid for subcell in row)

    return mapped_subcells >= 0.9 * total_subcells


def print_occupancy_grid(occupancy_grid):
    for row in occupancy_grid:
        print(' '.join(f'{subcell:.1f}' for subcell in row))




# def perform_mapping_task(controller, maze, max_time=180, grid_cell_size=10, subcell_size=2):
#     start_time = time.time()
#     occupancy_grid = initialize_occupancy_grid(grid_cell_size, subcell_size)

#     while time.time() - start_time < max_time:
#         #dsmove.wall_following(controller)
#         update_occupancy_grid(controller, occupancy_grid, grid_cell_size, subcell_size)

#         if is_90_percent_mapped(occupancy_grid):
#             break

#     print_occupancy_grid(occupancy_grid)
#     controller.stop()
#     return occupancy_grid

