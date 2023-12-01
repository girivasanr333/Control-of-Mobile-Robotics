#initialize motion probabities for the cells
def initialize_motion_probabilities():
    keys=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'];
    values=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0];
    motion_probabilities = dict(zip(keys, values));
    return(motion_probabilities);

# initialize visted_cells with '.'
def initialize_visited_cells():
    keys=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'];
    values=['.','.','.','.','.','.','.','.','.','.','.','.','.','.','.','.'];
    visited_cells = dict(zip(keys, values));
    return(visited_cells)

# motion probabilities
forward_motion_prob=0.8;
stay_motion_prob=0.2;

# Sensor model probabilities
p_z1_s1 = 0.9  # P(sensor='wall' | state='wall')
p_z0_s1 = 0.1  # P(sensor='no wall' | state='wall')
p_z0_s0 = 0.7  # P(sensor='no wall' | state='no wall')
p_z1_s0 = 0.3 # P(sensor='wall' | state='no wall')

maze3_prob=[0]*16;
# normalize state probabilities
def normalize_state_probabilities(measure_probabilities):
    #find the sum of all cells probabilities
    sum_prob=0.0;
    for cell in measure_probabilities:
        sum_prob=round(sum_prob+measure_probabilities[cell],2);
    #print(sum_prob);
    
    for cell in measure_probabilities:
        measure_probabilities[cell]=round(measure_probabilities[cell]/sum_prob,2);
    
    return(measure_probabilities);

# reset the Measure probailities
def reset_measure_probabilities(measure_probabilities):
    for cell in measure_probabilities:
        measure_probabilities[cell]=0.00;
    return(measure_probabilities);

# Update state probabilities with motion and measure probabilities and normalize

def update_state_probabilities(motion_probabilities,current,front_cell,front_z,front_s,visited_cells):

    # reset measure probabilities
    measure_probabilities = {};
    
    # decide the measure probability based on the wall state and sensor readings
    if front_z == 0 and front_s==0:
        sensor_prob = p_z0_s0;
    elif front_z == 0 and front_s==1:
        sensor_prob = p_z0_s1;
    elif front_z == 1 and front_s==0:
        sensor_prob = p_z1_s0;
    elif front_z == 1 and front_s==1:
        sensor_prob = p_z1_s1;
     
    if motion_probabilities[current] ==0:
        motion_probabilities[current] = stay_motion_prob;
        if front_cell != '0':
                motion_probabilities[front_cell]= forward_motion_prob;
    else:
        if front_cell != '0':
            motion_probabilities[front_cell]= round(motion_probabilities[current]*forward_motion_prob,2);
              
        motion_probabilities[current] = round(motion_probabilities[current]*stay_motion_prob,2);
    
     
    # Update the motion probabilities for the visited cells
    for each in visited_cells:
        if visited_cells[each] == 'x':
            if each != current and each != front_cell:
                motion_probabilities[each] = round(motion_probabilities[each]*stay_motion_prob,2);
    
    # multiply the motion probabilities with measure probabilities for each cell
    for each in motion_probabilities:
        measure_probabilities.update({each : round(motion_probabilities[each]*sensor_prob,2)});
        
    # normalize and update probabilities
    normalized_prob =normalize_state_probabilities(measure_probabilities);
    maze3_prob.append(measure_probabilities);
    #print(normalized_prob);
    
    #return the cumulative motion probabilities for next move
    return(motion_probabilities);


# code for testing
def maze3_probabilities():
    state_prob=initialize_motion_probabilities();
    visited_cells = initialize_visited_cells();
    maze3_cell_seq =[];

    update_prob=update_state_probabilities(state_prob,'16', '12',0,0,visited_cells);
    visited_cells.update({'16': 'x', '12': 'x'})
    maze3_cell_seq.append(16);
    maze3_cell_seq.append(12);  
    update_prob=update_state_probabilities(state_prob,'12', '8',0,0,visited_cells);
    visited_cells.update({'8':'x'});
    maze3_cell_seq.append(8);
    update_prob=update_state_probabilities(state_prob,'8', '4',0,0,visited_cells);
    visited_cells.update({'4':'x'});
    maze3_cell_seq.append(4);
    update_prob=update_state_probabilities(state_prob,'4', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'4', '3',0,0,visited_cells);#make a left turn
    visited_cells.update({'3':'x'});
    maze3_cell_seq.append(3);
    update_prob=update_state_probabilities(state_prob,'3', '2',0,0,visited_cells);
    visited_cells.update({'2':'x'});
    maze3_cell_seq.append(2);
    update_prob=update_state_probabilities(state_prob,'2', '1',0,0,visited_cells);
    visited_cells.update({'1':'x'});
    maze3_cell_seq.append(1);
    update_prob=update_state_probabilities(state_prob,'1', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'1', '2',0,0,visited_cells); #make a 360 turn
    visited_cells.update({'2':'x'});
    maze3_cell_seq.append(2);
    update_prob=update_state_probabilities(state_prob,'2', '3',0,0,visited_cells);
    visited_cells.update({'3':'x'});
    maze3_cell_seq.append(3);
    update_prob=update_state_probabilities(state_prob,'3', '7',0,0,visited_cells);
    visited_cells.update({'7':'x'});
    maze3_cell_seq.append(7);
    #update_prob=update_state_probabilities(state_prob,'7', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'7', '11',0,0,visited_cells); # make a right turn
    visited_cells.update({'11':'x'});
    maze3_cell_seq.append(11);
    #update_prob=update_state_probabilities(state_prob,'11', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'11', '10',0,0,visited_cells); # make a right turn
    visited_cells.update({'10':'x'});
    maze3_cell_seq.append(10);
    #update_prob=update_state_probabilities(state_prob,'10', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'10', '6',0,0,visited_cells); # make a right turn
    visited_cells.update({'6':'x'});
    maze3_cell_seq.append(6);
    #update_prob=update_state_probabilities(state_prob,'6', '0',1,1,visited_cells);
    update_prob=update_state_probabilities(state_prob,'6', '5',0,0,visited_cells); # make a left turn
    visited_cells.update({'5':'x'});
    maze3_cell_seq.append(5);
    #update_prob=update_state_probabilities(state_prob,'5', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'5', '9',0,0,visited_cells); # make a right turn
    visited_cells.update({'9':'x'});
    maze3_cell_seq.append(9);
    update_prob=update_state_probabilities(state_prob,'9', '13',0,0,visited_cells);
    visited_cells.update({'13':'x'});
    maze3_cell_seq.append(13);
    #update_prob=update_state_probabilities(state_prob,'13', '0',1,1,visited_cells);

    update_prob=update_state_probabilities(state_prob,'13', '14',0,0,visited_cells); #make a right turn
    visited_cells.update({'14':'x'});
    maze3_cell_seq.append(14);
    update_prob=update_state_probabilities(state_prob,'14', '15',0,0,visited_cells);
    visited_cells.update({'15':'x'});
    maze3_cell_seq.append(15);
    update_prob=update_state_probabilities(state_prob,'15', '16',0,0,visited_cells);
    visited_cells.update({'16':'x'});
    maze3_cell_seq.append(16);

    print(" Maze3 probabilities for each move:")
    for each in maze3_prob:
        if each !=0:
            print(each);
    
    print("Maze3 cell sequence");
    print(maze3_cell_seq);

    return();


maze3_probabilities();