"""
This function sets up screen display and task structs for training version.
"""

import numpy as np
import random
from datetime import datetime
from pathlib import Path
from psychopy import visual, monitors, event
from psychopy.hardware import keyboard

from get_instruction_text import get_instruction_text
# from init_cedrus import init_cedrus  # Commented out - using keyboard only

def init_task_training():
    """
    Initialize task and display structures for training.
    
    Returns:
    --------
    task_struct : dict
        Dictionary containing all task parameters
    disp_struct : dict
        Dictionary containing display parameters and window handles
    """
    # Some initial global setup
    np.random.seed()
    
    # Get user input
    sub_id = input('Participant number (PxxCS):\n')
    eye_link_mode = int(input('Use Eyelink? 0=no, 1=yes:\n'))
    # use_cedrus = int(input('Use CEDRUS? 0=no, 1=yes:\n'))  # Commented out - using keyboard only
    use_cedrus = 0  # Always use keyboard (arrow keys)
    debug = int(input('Debug mode? 0=no, 1=yes:\n'))
    
    # Uncomment for quick testing:
    # sub_id = '0'
    # eye_link_mode = 0
    # use_cedrus = 0
    # debug = 1
    
    # Output folder
    output_folder = Path('..') / 'patientData' / 'trainingLogs'
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{sub_id}_training_Sub_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}"
    
    # Setting up task variables
    n_blocks = 1
    n_trials_per_block = 16
    n_trials = n_trials_per_block * n_blocks
    
    # Trial conditions: 1 = instruction first; 2 = instruction in the middle
    trial_conditions = [1] * (n_trials_per_block // 2) + [2] * (n_trials_per_block // 2)
    
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
    trial_categories = [1, 2]  # Only Cars and Faces for training (0-indexed: 1=Cars, 2=Faces)
    trial_axis = [0, 1]
    anti_task = [0, 1]
    equivalent_variant_id = [0, 1]
    
    # Guaranteeing a balanced distribution
    from itertools import product
    combinations = list(product(trial_categories, trial_axis, anti_task, equivalent_variant_id))
    n = len(combinations)
    factor = n_trials // n
    result = combinations * factor
    if len(result) < n_trials:
        result.extend(combinations[:n_trials - len(result)])
    
    # Randomize trial order
    random.shuffle(result)
    
    trial_categories = [r[0] for r in result]
    trial_axis_list = [r[1] for r in result]
    anti_task = [r[2] for r in result]
    equivalent_variant_id = [r[3] for r in result]
    
    # Ensuring that first trials are easier
    anti_task[:5] = [0] * 5
    equivalent_variant_id[:5] = [1] * 5
    
    # For instructions, use only one prompt variant
    prompt_variant = [1] * n_trials
    
    # Determining which stimuli to use in each trial
    stim_folder = Path('..') / 'stimuli' / 'Training_Stim'
    trial_stims = [[None, None] for _ in range(n_trials)]
    trial_pairs = np.zeros(n_trials, dtype=int)
    stim1_position = np.full(n_trials, np.nan)
    stim2_position = np.full(n_trials, np.nan)
    break_trial = np.zeros(n_trials, dtype=int)
    
    # Filling trial cells with pair numbers
    pair_numbers = {}
    for i in trial_axis:  # 2 axes
        for j in trial_categories:  # Only Cars and Faces
            pair_numbers[(i, j)] = list(range(6)) * 4  # 6 pairs (0-5) x 4 repetitions
    
    # Filling identical cells
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
    
    # Trial loop to set up stimuli and instructions
    for t_i in range(n_trials):
        axis = trial_axis_list[t_i]
        category = trial_categories[t_i]
        
        # Selecting one pair number
        sampled_vector = pair_numbers[(axis, category)]
        if len(sampled_vector) == 1:
            sampled_vector = sampled_vector * 2
        trial_pair = random.choice(sampled_vector)
        trial_pairs[t_i] = trial_pair
        pair_numbers[(axis, category)].remove(trial_pair)
        
        # Determining if this is an identical stimulus trial
        identical_trial = False
        if axis_names[category][axis] == 'Identical':
            if identical_trials_for_replacement[category]:
                identical_trial = identical_trials_for_replacement[category].pop()
        
        # Loading stimuli
        trial_folder = stim_folder / category_names[category] / f'Pair{trial_pair + 1}'
        folder_images = list(trial_folder.glob('*.jpg'))
        if len(folder_images) == 0:
            folder_images = list(trial_folder.glob('*.JPG'))
        
        sampled_images = random.sample(folder_images, min(2, len(folder_images)))
        trial_stims[t_i][0] = str(sampled_images[0])
        trial_stims[t_i][1] = str(sampled_images[1]) if len(sampled_images) > 1 else str(sampled_images[0])
        
        if axis_names[category][axis] == 'Identical' and identical_trial:
            trial_stims[t_i][1] = str(sampled_images[0])
        
        stim1_position[t_i] = 3
        stim2_position[t_i] = 3
        
        if (t_i + 1) % n_trials_per_block == 0 and t_i < n_trials - 1:
            break_trial[t_i] = 1
        
        # Instructions
        trial_axis_name = axis_names[category][axis]
        trial_instructions = get_instruction_text(
            category, trial_axis_name, anti_task[t_i],
            prompt_variant[t_i], equivalent_variant_id[t_i]
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
        'stim_folder': stim_folder,
        'trial_stims': trial_stims,
        'trial_pairs': trial_pairs,
        'stim1_position': stim1_position,
        'stim2_position': stim2_position,
        'break_trial': break_trial,
        'left_text': left_text,
        'right_text': right_text,
        'fixation_time': 1.0,
        'instruction_time_min': 2.5,
        'instruction_time_max': 4.0,
        'stim1_time': 1.0,
        'ISI': 0.8,
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
    
    # Setting up input devices
    # CEDRUS button box code commented out - using keyboard only
    # if task_struct['use_cedrus']:
    #     task_struct['handle'] = init_cedrus()
    #     task_struct['left_key'] = 4
    #     task_struct['right_key'] = 5
    #     task_struct['confirm_key'] = 3
    # else:
    task_struct['handle'] = None
    task_struct['left_key'] = 'left'  # Left arrow key
    task_struct['right_key'] = 'right'  # Right arrow key
    task_struct['confirm_key'] = 'space'
    
    task_struct['escape_key'] = 'q'
    task_struct['pause_key'] = 'p'
    task_struct['continue_key'] = 'c'
    
    # Creating display struct (same as main task)
    disp_struct = {}
    
    if debug:
        screen_size = [800, 600]
        full_screen = False
    else:
        screen_size = None
        full_screen = True
    
    gray = [0.31, 0.31, 0.31]
    
    win = visual.Window(
        size=screen_size,
        fullscr=full_screen,
        screen=0,
        color=gray,
        units='pix',
        allowGUI=not full_screen
    )
    
    center_x = win.size[0] / 2
    center_y = win.size[1] / 2
    width = win.size[0]
    height = win.size[1]
    
    dx = width / 12
    dy = height / 5
    
    stim_size = 250
    rew_width = 466
    rew_height = 350
    ph = stim_size
    pw = stim_size
    rw = rew_width
    rh = rew_height
    
    vertical_rects = [
        [center_x - pw/2, center_y - dy - ph/2, center_x + pw/2, center_y - dy + ph/2],
        [center_x - pw/2, center_y + dy - ph/2, center_x + pw/2, center_y + dy + ph/2]
    ]
    
    horizontal_rects = [
        [center_x - dx - pw/2, center_y - ph/2, center_x - dx + pw/2, center_y + ph/2],
        [center_x + dx - pw/2, center_y - ph/2, center_x + dx + pw/2, center_y + ph/2],
        [center_x - rw/2, center_y - rh/2, center_x + rw/2, center_y + rh/2]
    ]
    
    reward_source_rect = [160, 0, 1120, 720]
    
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

