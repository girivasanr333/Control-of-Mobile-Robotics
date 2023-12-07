import math
import numpy as np

p_list = {1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{},12:{},13:{},14:{},15:{},16:{}}
l_list={1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{},12:{},13:{},14:{},15:{},16:{}}

maze1_front_cell_list={16:{12,8,4}, 12:{8,4},8:{4}, 4:{3,2,1}, 3:{2,1}, 2:{1}, 1: {5}, 5:{6,7}, 6:{7},7:{11}, 11:{10,9}, 10:{9}, 9:{13}, 13: {14,15,16}, 14:{15,16}, 15:{16}}
maze1_cell_behind_wall={1:9,2:0,3:0,4:0,5:8,6:8, 7:15,11:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0}
maze1_wall_cell={16:4, 12:4,8:4,4:1,3:1,2:1, 1:5, 5:7, 6:7, 7:11, 11:9, 10:9,9:13,13:16,14:16,15:16}

maze3_front_cell_list={16:{12,8,4}, 12:{8,4},8:{4}, 4:{3,2,1}, 1: {2,3,4}, 3:{7,11}, 2:{3}, 7:{11}, 11:{10}, 10:{6}, 6:{5}, 5:{9,13}, 9:{13}, 13: {14,15,16}, 14:{15,16},15:{16}}
maze3_cell_behind_wall={1:0,2:0,3:15,4:0,5:0,6:0,7:15,8:0,9:0,10:2,11:9,12:0,13:0,14:0,15:0,16:0}
maze3_wall_cell={16:4, 12:4,8:4,4:1,3:11,2:0, 1:0, 5:13, 6:5, 7:11, 11:10, 10:6,9:13,13:16,14:16,15:16}

l0=0
gridmap={1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{},12:{},13:{},14:{},15:{},16:{}}


def initialize_gridmap():
    for i in range (1,17):
        for j in range (1,26):
            gridmap[i].update({j: 0.5})
        #gridmap.append(gridcell)
    return    

def initialize_l():
    for i in range (1,17):
        for j in range (1,26):
            l_list[i].update({j: 0.0})
    return   

def initialize_p():
    for i in range (1,17):
        for j in range (1,26):
            p_list[i].update({j: 0.5})
    return    

def maze1_occupancy_mapping_update(gridmap,current_cell):
    
    
    l0=0
    # updating cells lesser than wall measured cells
    front_cell_list=[]
    for i in range(1,26):
        gridmap[current_cell].update({i:0.3})    
    front_cell_list= maze1_front_cell_list[current_cell]
    
    for each in front_cell_list:
        #print(each)                             
        for i in range(1,26):
            gridmap[each].update({i:0.3})
                                 
    # updating cells next to wall measured
    #print(maze1_wall_cell[wall_cell])
    
    wall_cell=maze1_cell_behind_wall[current_cell]
    
    if wall_cell != 0:
        for i in range(1,26):
            gridmap[wall_cell].update({i:0.6})
                                 
    #Updating l values
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            temp= math.log(gridmap[i][j]/(1-gridmap[i][j]))
            l_list[i].update({j: round(temp+prev-l0,3)})
            
    #print ("Printing L values")
    #print(l_list)
    
    #updating p values
    
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            #print(prev)
            temp= 1/(1+math.exp(l_list[i][j]))
            #print(math.log(temp))
            p_list[i].update({j: round(1-temp,3)})
    
    print ("\n")
    print(p_list)
   
    return

def maze3_occupancy_mapping_update(gridmap,current_cell):
    l0=0
    # updating cells lesser than wall measured cells
    front_cell_list=[]
    for i in range(1,26):
        gridmap[current_cell].update({i:0.3})    
    front_cell_list= maze3_front_cell_list[current_cell]
    for each in front_cell_list:
        #print(each)                             
        for i in range(1,26):
            gridmap[each].update({i:0.3})
                                 
    # updating cells next to wall measured
    #print(maze1_wall_cell[wall_cell])
    wall_cell=maze3_cell_behind_wall[current_cell]
    if wall_cell != 0:
        for i in range(1,26):
            gridmap[wall_cell].update({i:0.6})
                                 
    #Updating l values
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            temp= math.log(gridmap[i][j]/(1-gridmap[i][j]))
            l_list[i].update({j: round(temp+prev-l0,3)})
            
    
    #print ("Printing L values")
    #print(l_list)
    
    #updating p values
    
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            #print(prev)
            temp= 1/(1+math.exp(l_list[i][j]))
            #print(math.log(temp))
            p_list[i].update({j: round(1-temp,3)})
    
    print ("\n")
    print(p_list)
   
    return

def maze1_occupancy_mapping_update_4x4(gridmap,current_cell):
    
    l0=0
    # updating cells lesser than wall measured cells
    front_cell_list=[]
    for i in range(1,26):
        gridmap[current_cell].update({i:0.3})    
    front_cell_list= maze1_front_cell_list[current_cell]
    
    for each in front_cell_list:
        #print(each)                             
        for i in range(1,26):
            gridmap[each].update({i:0.3})
                                 
    # updating cells next to wall measured
    #print(maze1_wall_cell[wall_cell])
    
    wall_cell=maze1_cell_behind_wall[current_cell]
    
    if wall_cell != 0:
        for i in range(1,26):
            gridmap[wall_cell].update({i:0.6})
                                 
    #Updating l values
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            temp= math.log(gridmap[i][j]/(1-gridmap[i][j]))
            l_list[i].update({j: round(temp+prev-l0,3)})
            
    #print ("Printing L values")
    #print(l_list)
    
    #updating p values
    
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            #print(prev)
            temp= 1/(1+math.exp(l_list[i][j]))
            #print(math.log(temp))
            p_list[i].update({j: round(1-temp,3)})
    
    print ("Printing p values")
    for i in range (1,17):
        print(str(i)+":  "+str(p_list[i][1]))
    
    return

def maze3_occupancy_mapping_update_4x4(gridmap,current_cell):
    l0=0
    # updating cells lesser than wall measured cells
    front_cell_list=[]
    for i in range(1,26):
        gridmap[current_cell].update({i:0.3})    
    front_cell_list= maze3_front_cell_list[current_cell]
    for each in front_cell_list:
        #print(each)                             
        for i in range(1,26):
            gridmap[each].update({i:0.3})
                                 
    # updating cells next to wall measured
    #print(maze1_wall_cell[wall_cell])
    wall_cell=maze3_cell_behind_wall[current_cell]
    if wall_cell != 0:
        for i in range(1,26):
            gridmap[wall_cell].update({i:0.6})
                                 
    #Updating l values
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            temp= math.log(gridmap[i][j]/(1-gridmap[i][j]))
            l_list[i].update({j: round(temp+prev-l0,3)})
            
    
    #print ("Printing L values")
    #print(l_list)
    
    #updating p values
    
    for i in range(1,17):
        for j in range(1,26):
            prev=l_list[i][j]
            #print(prev)
            temp= 1/(1+math.exp(l_list[i][j]))
            #print(math.log(temp))
            p_list[i].update({j: round(1-temp,3)})
    
    print ("Printing p values")
    for i in range (1,17):
        print(str(i)+":  "+str(p_list[i][1]))
    
    return

# Code for testing
initialize_gridmap()
initialize_l()
initialize_p()

#maze 1 printing p values after each detection of th wall
'''
print("Printing Maze1 p values")

maze1_occupancy_mapping_update(gridmap,16)
maze1_occupancy_mapping_update(gridmap,4)
maze1_occupancy_mapping_update(gridmap,1)
maze1_occupancy_mapping_update(gridmap,5)
maze1_occupancy_mapping_update(gridmap,7)
maze1_occupancy_mapping_update(gridmap,11)
maze1_occupancy_mapping_update(gridmap,9)
maze1_occupancy_mapping_update(gridmap,13)
'''
'''
#maze 3 printing p values after each detection of th wall
print("Printing Maze3 p values")
maze3_occupancy_mapping_update(gridmap,16)
maze3_occupancy_mapping_update(gridmap,4)
maze3_occupancy_mapping_update(gridmap,1)
maze3_occupancy_mapping_update(gridmap,3)
maze3_occupancy_mapping_update(gridmap,11)
maze3_occupancy_mapping_update(gridmap,10)
maze3_occupancy_mapping_update(gridmap,6)
maze3_occupancy_mapping_update(gridmap,5)
maze3_occupancy_mapping_update(gridmap,13)
'''

'''
print("Printing Maze1 p values")

maze1_occupancy_mapping_update_4x4(gridmap,16)
maze1_occupancy_mapping_update_4x4(gridmap,4)
maze1_occupancy_mapping_update_4x4(gridmap,1)
maze1_occupancy_mapping_update_4x4(gridmap,5)
maze1_occupancy_mapping_update_4x4(gridmap,7)
maze1_occupancy_mapping_update_4x4(gridmap,11)
maze1_occupancy_mapping_update_4x4(gridmap,9)
maze1_occupancy_mapping_update_4x4(gridmap,13)

'''
#maze 3 printing p values after each detection of th wall
print("Printing Maze3 p values")
maze3_occupancy_mapping_update_4x4(gridmap,16)
maze3_occupancy_mapping_update_4x4(gridmap,4)
maze3_occupancy_mapping_update_4x4(gridmap,1)
maze3_occupancy_mapping_update_4x4(gridmap,3)
maze3_occupancy_mapping_update_4x4(gridmap,11)
maze3_occupancy_mapping_update_4x4(gridmap,10)
maze3_occupancy_mapping_update_4x4(gridmap,6)
maze3_occupancy_mapping_update_4x4(gridmap,5)
maze3_occupancy_mapping_update_4x4(gridmap,13)
