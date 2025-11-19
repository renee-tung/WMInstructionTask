"""
This function sets up screen display and task structs which will contain
important task information.
"""

import numpy as np
import random
from datetime import datetime
from pathlib import Path
from psychopy import visual, monitors, event
from psychopy.hardware import keyboard

from get_instruction_text import get_instruction_text
from get_motor_instruction_text import get_motor_instruction_text
from get_correct_responses import get_correct_responses
from init_cedrus import init_cedrus

def init_task():
    """
    Initialize task and display structures.
    
    Returns:
    --------
    task_struct : dict
        Dictionary containing all task parameters
    disp_struct : dict
        Dictionary containing display parameters and window handles
    """
    # Some initial global setup
    np.random.seed()  # Use system time as seed
    
    # Get user input
    sub_id = input('Participant number (PxxCS):\n')
    eye_link_mode = int(input('Use Eyelink? 0=no, 1=yes:\n'))
    use_cedrus = int(input('Use CEDRUS? 0=no, 1=yes:\n'))
    debug = int(input('Debug mode? 0=no, 1=yes:\n'))
    
    # Uncomment for quick testing:
    # sub_id = '0'
    # eye_link_mode = 0
    # use_cedrus = 0
    # debug = 1
    
    # Output folder
    output_folder = Path('..') / 'patientData' / 'taskLogs'
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{sub_id}_Sub_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}"
    
    # Setting up task variables
    n_blocks = 4
    n_trials_per_block = 48
    n_trials = n_trials_per_block * n_blocks
    
    # Trial conditions: 1 = instruction first; 2 = instruction last (retrocue)
    trial_conditions = np.concatenate([
            2 * np.ones(n_trials_per_block, dtype=int),
            np.ones(n_trials_per_block, dtype=int),
            2 * np.ones(n_trials_per_block, dtype=int),
            np.ones(n_trials_per_block, dtype=int),
        ])
    
    # Relevant axis of each trial
    category_names = ['Animals', 'Cars', 'Faces', 'Fruits']
    axis_names = [
        ['Colorful', 'Count'],
        ['New', 'Colorful'],
        ['New', 'Identical'],
        ['Count', 'Identical']
    ]
    category_and_axis = [category_names, axis_names]
    
    # Which of the two axes belonging to each category will be used in each trial
    trial_categories = [0, 1, 2, 3]
    trial_axis = [0, 1]
    # anti_task = [0, 1]
    anti_task = [0] # getting rid of the anti-task
    prompt_variant = [0, 1]
    equivalent_variant_id = [0, 1]
    response_variant = [0, 1] # button choice vs slider
    
    # Guaranteeing a balanced distribution of each category x axis combination
    x1, x2, x3, x4, x5, x6 = np.meshgrid(trial_categories, trial_axis, anti_task, prompt_variant, equivalent_variant_id, response_variant, indexing='ij')
    result = np.column_stack([x1.ravel(), x2.ravel(), x3.ravel(), x4.ravel(), x5.ravel(), x6.ravel()])
    n = result.shape[0]
    factor = n_trials // n
    result = result * factor
    if len(result) < n_trials:
        result = np.concatenate([result, result[:n_trials - len(result)]])
    
    # Randomize trial order
    result = np.random.permutation(result) 
    
    trial_categories = result[:, 0]
    trial_axis_list = result[:, 1]
    anti_task = result[:, 2]
    prompt_variant = result[:, 3]
    equivalent_variant_id = result[:, 4]
    response_variant = result[:, 5]
    
    # Determining which stimuli to use in each trial
    stim_folder = Path('..') / 'stimuli' / 'Task_Stim_Version2'
    trial_stims = [[None, None] for _ in range(n_trials)]
    trial_pairs = np.zeros(n_trials, dtype=int)
    stim1_position = np.full(n_trials, np.nan)
    stim2_position = np.full(n_trials, np.nan)
    break_trial = np.zeros(n_trials, dtype=int)

    # Hard code number of pairs and repetitions given task time constraints
    n_pairs = 6
    n_repetitions = 4
    
    # Filling trial cells with pair numbers to be drawn from (without replacement)
    pair_numbers = {}
    for i in trial_axis:  # 2 axes
        for j in trial_categories:  # 4 categories
            pair_numbers[(i, j)] = list(range(n_pairs)) * n_repetitions  # n_pairs (0-n_pairs-1) x n_repetitions repetitions
    
    # Filling identical cells with identical trials to be drawn from (without replacement)
    identical_trials = {}
    for i, axes in enumerate(axis_names):
        if 'Identical' in axes:
            idx = [0] * (n_trials_per_block // 4) + [1] * (n_trials_per_block // 4)
            random.shuffle(idx)
            identical_trials[i] = idx
    identical_trials_for_replacement = {k: v.copy() for k, v in identical_trials.items()}
    
    # Response prompts
    prompt_types = [random.randint(1, 2) for _ in range(n_trials)]
    left_text = [None] * n_trials
    right_text = [None] * n_trials
    trial_instructions = [None] * n_trials
    response_instructions = [None] * n_trials
    
    # Trial loop to set up stimuli and instructions
    for t_i in range(n_trials):
        axis = trial_axis_list[t_i]
        category = trial_categories[t_i]
        
        # Selecting one pair number from pair cell and removing it (no replacement)
        sampled_vector = pair_numbers[(axis, category)]
        if len(sampled_vector) == 1:
            sampled_vector = sampled_vector * 2
        trial_pair = random.choice(sampled_vector)
        trial_pairs[t_i] = trial_pair
        # Remove one occurrence
        pair_numbers[(axis, category)].remove(trial_pair)
        
        # Determining if this is an identical stimulus trial in the identical axis
        identical_trial = False
        if axis_names[category][axis] == 'Identical':
            if identical_trials_for_replacement[category]:
                identical_trial = identical_trials_for_replacement[category].pop()
        
        # Loading stimuli
        trial_folder = stim_folder / category_names[category] / f'Pair{trial_pair + 1}'
        folder_images = list(trial_folder.glob('*.jpg'))
        if len(folder_images) == 0:
            folder_images = list(trial_folder.glob('*.JPG'))
        
        # Sampling 2 random images from folder (without replacement)
        sampled_images = random.sample(folder_images, min(2, len(folder_images)))
        trial_stims[t_i][0] = str(sampled_images[0])
        trial_stims[t_i][1] = str(sampled_images[1]) if len(sampled_images) > 1 else str(sampled_images[0])
        
        # Keeping first image equal to second in identical trials
        if axis_names[category][axis] == 'Identical' and identical_trial:
            trial_stims[t_i][1] = str(sampled_images[0])
        
        # Randomly select position of stimuli (1 = left / 2 = right / 3 = center)
        stim1_position[t_i] = 3
        stim2_position[t_i] = 3
        
        if (t_i + 1) % n_trials_per_block == 0 and t_i < n_trials - 1:
            break_trial[t_i] = 1
        
        # Instructions for task
        trial_axis_name = axis_names[category][axis]
        trial_instructions[t_i] = get_instruction_text(
            category, trial_axis_name, anti_task[t_i],
            prompt_variant[t_i], equivalent_variant_id[t_i]
        )
        
        # Instructions for response
        response_instructions[t_i] = get_motor_instruction_text(
            response_variant[t_i]
        )

        # Response prompts
        if trial_axis_name != 'Identical':
            if prompt_types[t_i] == 1:
                left_text[t_i] = 'First'
                right_text[t_i] = 'Second'
            else:
                left_text[t_i] = 'Second'
                right_text[t_i] = 'First'
        else:
            if prompt_types[t_i] == 1:
                left_text[t_i] = 'Yes'
                right_text[t_i] = 'No'
            else:
                left_text[t_i] = 'No'
                right_text[t_i] = 'Yes'
    
    # Create task struct
    task_struct = {
        'sub_id': sub_id,
        'eye_link_mode': bool(eye_link_mode),
        'use_cedrus': bool(use_cedrus),
        'debug': bool(debug),
        'output_folder': output_folder,
        'file_name': file_name,
        'n_blocks': n_blocks,
        'n_trials_per_block': n_trials_per_block,
        'n_trials': n_trials,
        'trial_conditions': trial_conditions,
        'category_names': category_names,
        'axis_names': axis_names,
        'category_and_axis': category_and_axis,
        'trial_categories': trial_categories,
        'trial_axis': trial_axis_list,
        'anti_task': anti_task,
        'prompt_variant': prompt_variant,
        'equivalent_variant_id': equivalent_variant_id,
        'response_variant': response_variant,
        'trial_instructions': trial_instructions,
        'response_instructions': response_instructions,
        'prompt_types': prompt_types,
        'stim_folder': stim_folder,
        'trial_stims': trial_stims,
        'trial_pairs': trial_pairs,
        'n_pairs': n_pairs,
        'n_repetitions': n_repetitions,
        'stim1_position': stim1_position,
        'stim2_position': stim2_position,
        'break_trial': break_trial,
        'left_text': left_text,
        'right_text': right_text,
        'fixation_time': 1.0,
        'instruction_time_min': 2.5,
        'instruction_time_max': 4.0,
        'stim1_time': 1.0,
        'ISI': 2.0, # changed from 0.8
        'stim2_time': 1.0,
        'response_time_max': 3.0,
        'text_holdout_time': 0.5,
        'ITI': 1.0,
        'instruction_time': np.full(n_trials, np.nan),
        'response_time': np.full(n_trials, np.nan),
        'trial_time': np.full(n_trials, np.nan),
        'resp_key': np.full(n_trials, np.nan),
        'complete_flag': 1,
    }
    
    # Get correct responses
    task_struct['correct_responses'] = get_correct_responses(task_struct)
    
    # Setting up input devices
    if task_struct['use_cedrus']:
        task_struct['handle'] = init_cedrus()
        task_struct['left_key'] = 4
        task_struct['right_key'] = 5
        task_struct['confirm_key'] = 3
    else:
        task_struct['handle'] = None
        task_struct['left_key'] = 'left'  # Left arrow key
        task_struct['right_key'] = 'right'  # Right arrow key
        task_struct['confirm_key'] = 'space'
    
    task_struct['escape_key'] = 'q'
    task_struct['pause_key'] = 'p'
    task_struct['continue_key'] = 'c'
    
    # Creating display struct
    disp_struct = {}
    
    # Getting screen information
    if debug:
        screen_size = [800, 600]
        full_screen = False
    else:
        screen_size = None
        full_screen = True
    
    # Define gray background
    gray = [0.31, 0.31, 0.31]  # RGB equivalent of 80/255
    
    # Opening window
    win = visual.Window(
        size=screen_size,
        fullscr=full_screen,
        screen=0,
        color=gray,
        units='pix',
        allowGUI=not full_screen
    )
    
    # Getting screen center and dimensions
    center_x = win.size[0] / 2
    center_y = win.size[1] / 2
    width = win.size[0]
    height = win.size[1]
    
    dx = width / 12
    dy = height / 5
    
    # Size of figures on screen, in pixels (4:3)
    stim_size = 250
    rew_width = 466
    rew_height = 350
    ph = stim_size
    pw = stim_size
    rw = rew_width
    rh = rew_height
    
    # Setting up stimuli presentation rectangles
    # center top (1)
    vertical_rects = [
        [center_x - pw/2, center_y - dy - ph/2, center_x + pw/2, center_y - dy + ph/2],
        [center_x - pw/2, center_y + dy - ph/2, center_x + pw/2, center_y + dy + ph/2]
    ]
    
    # left center (1), right center (2), center (3)
    horizontal_rects = [
        [center_x - dx - pw/2, center_y - ph/2, center_x - dx + pw/2, center_y + ph/2],
        [center_x + dx - pw/2, center_y - ph/2, center_x + dx + pw/2, center_y + ph/2],
        [center_x - rw/2, center_y - rh/2, center_x + rw/2, center_y + rh/2]
    ]
    
    reward_source_rect = [160, 0, 1120, 720]  # Portion of reward videos displayed
    
    disp_struct['win'] = win
    disp_struct['screen_number'] = 0
    disp_struct['center_x'] = center_x
    disp_struct['center_y'] = center_y
    disp_struct['width'] = width
    disp_struct['height'] = height
    disp_struct['stim_size'] = stim_size
    disp_struct['rew_width'] = rew_width
    disp_struct['rew_height'] = rew_height
    disp_struct['reward_rect'] = horizontal_rects[2]
    disp_struct['reward_source_rect'] = reward_source_rect
    disp_struct['vertical_rects'] = vertical_rects
    disp_struct['horizontal_rects'] = horizontal_rects
    
    return task_struct, disp_struct

