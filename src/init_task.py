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

from src.get_instruction_text import get_instruction_text
from src.get_motor_instruction_text import get_motor_instruction_text
from src.get_correct_responses import get_correct_responses
from src.init_cedrus import init_cedrus # commented out - CEDRUS not used in training

import pdb

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
    sub_id = input('Participant number (XXX):\n')
    blackrock_enabled = int(input('Blackrock comments enabled? 0=no, 1=yes:\n'))
    eye_link_mode = int(input('Use Eyelink? 0=no, 1=yes:\n'))
    use_cedrus = int(input('Use CEDRUS? 0=no, 1=yes:\n'))
    debug = int(input('Debug mode? 0=no, 1=yes:\n'))
    
    # Output folder
    output_folder = Path('..') / 'patientData' / 'taskLogs'
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{sub_id}_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}"
    
    # Setting up task variables
    n_blocks = 4
    n_trials_per_block = 48
    n_trials = n_trials_per_block * n_blocks
    
    # Relevant axis of each trial
    category_names = ['Animals', 'Cars', 'Faces', 'Fruits']
    axis_names = [
        ['Colorful', 'Count'],
        ['New', 'Colorful'],
        ['New', 'Geometry'],
        ['Count', 'Geometry']
    ]
    category_and_axis = [category_names, axis_names]
    
    # Which of the two axes belonging to each category will be used in each trial
    trial_categories = [0, 1, 2, 3] # 4 categories
    trial_axis = [0, 1] # 2 axes
    stim_pairs = [0, 1, 2] # 3 pairs of stimuli per category/axis
    prompt_variants = [0, 1] # which prompt version to use (aspect of the axis)
    response_variants = [0, 1] # button choice vs slider
    cue_variants = [2, 1] # retrocue vs cue

    n_categories = len(trial_categories)
    n_response_variants = len(response_variants)
    
    # Guaranteeing a balanced distribution of each category x axis combination
    x1, x2, x3, x4, x5, x6 = np.meshgrid(trial_categories, trial_axis, stim_pairs, prompt_variants, response_variants, cue_variants, indexing='ij')
    result = np.column_stack([x1.ravel(), x2.ravel(), x3.ravel(), x4.ravel(), x5.ravel(), x6.ravel()])
    n = result.shape[0]
    factor = n_trials // n
    # result = result * factor
    result = np.repeat(result, factor, axis=0)
    if len(result) < n_trials:
        result = np.concatenate([result, result[:n_trials - len(result)]])
    
    # Randomize trial order
    result = np.random.permutation(result) 

    retro_block1, retro_block2 = make_blocks_for_cue(result, cue_value=2, 
                                                            n_categories=n_categories, n_response_variants=n_response_variants, 
                                                            rng=None)
    cue_block1, cue_block2 = make_blocks_for_cue(result, cue_value=1, 
                                                                n_categories=n_categories, n_response_variants=n_response_variants, 
                                                                rng=None)
    
    # randomize which block to start with
    if random.random() < 0.5:
        sorted_idxs = np.concatenate([
            retro_block1,  # Block 1: retrocue
            cue_block1,    # Block 2: cue
            retro_block2,  # Block 3: retrocue
            cue_block2     # Block 4: cue
        ])
    else:
        sorted_idxs = np.concatenate([
            cue_block1,    # Block 1: cue
            retro_block1,  # Block 2: retrocue
            cue_block2,    # Block 3: cue
            retro_block2   # Block 4: retrocue
        ])

    # # Sort into 4 blocks by cue variant (retrocue, cue, retrocue, cue)
    # cue_variant = result[:, 5]
    # retrocue_idxs = np.where(cue_variant == 2)[0] # retrocue trial idxs
    # cue_idxs = np.where(cue_variant == 1)[0] # cue trial idxs
    # sorted_idxs = np.concatenate([retrocue_idxs[:n_trials_per_block],
    #                             cue_idxs[:n_trials_per_block],
    #                             retrocue_idxs[n_trials_per_block:],
    #                             cue_idxs[n_trials_per_block:]])
    
    result = result[sorted_idxs]

    # ensure no back-to-back same (category, stim_pair) within each block
    blocks = np.split(result, 4)
    fixed_blocks = [avoid_back_to_back_same_stim(b) for b in blocks]
    result = np.vstack(fixed_blocks)
    
    trial_categories = result[:, 0]
    trial_axis_list = result[:, 1]
    stim_pairs = result[:, 2]
    prompt_variants = result[:, 3]
    response_variants = result[:, 4]
    cue_variants = result[:, 5]
    
    # Getting stimuli to use in each trial
    stim_folder = Path('..') / 'stimuli' / 'Task_Stim_New_v1'
    trial_stims = [[None, None] for _ in range(n_trials)]
    stim1_position = np.full(n_trials, np.nan)
    stim2_position = np.full(n_trials, np.nan)
    break_trial = np.zeros(n_trials, dtype=int)
    
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
        stim_pair = stim_pairs[t_i]
        
        # Loading stimuli
        trial_folder = stim_folder / category_names[category] / f'Pair{stim_pair + 1}'
        folder_images = list(trial_folder.glob('*.jpg'))
        if len(folder_images) == 0:
            folder_images = list(trial_folder.glob('*.JPG'))
        
        # Sampling 2 random images from folder (without replacement)
        sampled_images = random.sample(folder_images, min(2, len(folder_images)))
        trial_stims[t_i][0] = str(sampled_images[0])
        trial_stims[t_i][1] = str(sampled_images[1]) if len(sampled_images) > 1 else str(sampled_images[0])
        
        # Randomly select position of stimuli (1 = left / 2 = right / 3 = center)
        stim1_position[t_i] = 3
        stim2_position[t_i] = 3
        
        if (t_i + 1) % n_trials_per_block == 0 and t_i < n_trials - 1:
            break_trial[t_i] = 1
        
        # Instructions for task
        trial_axis_name = axis_names[category][axis]
        trial_instructions[t_i] = get_instruction_text(
            category, trial_axis_name, prompt_variants[t_i]
        )
        
        # Instructions for response
        response_instructions[t_i] = get_motor_instruction_text(
            response_variants[t_i]
        )

        # Response prompts
        if prompt_types[t_i] == 1:
            left_text[t_i] = 'First'
            right_text[t_i] = 'Second'
        else:
            left_text[t_i] = 'Second'
            right_text[t_i] = 'First'

    # create time jitters
    fixations = np.random.uniform(0.9, 1.2, n_trials).round(3)
    delays = np.random.uniform(2, 2.4, n_trials).round(3)
    
    # Create task struct
    task_struct = {
        'sub_id': sub_id,
        'blackrock_enabled': bool(blackrock_enabled),
        'eye_link_mode': bool(eye_link_mode),
        'use_cedrus': bool(use_cedrus),
        'debug': bool(debug),
        'output_folder': output_folder,
        'file_name': file_name,
        'n_blocks': n_blocks,
        'n_trials_per_block': n_trials_per_block,
        'n_trials': n_trials,
        'trial_cues': cue_variants,
        'category_names': category_names,
        'axis_names': axis_names,
        'category_and_axis': category_and_axis,
        'trial_categories': trial_categories,
        'trial_axis': trial_axis_list,
        'prompt_variants': prompt_variants,
        'response_variants': response_variants,
        'trial_instructions': trial_instructions,
        'response_instructions': response_instructions,
        'prompt_types': prompt_types,
        'stim_folder': stim_folder,
        'trial_stims': trial_stims,
        'trial_pairs': stim_pairs,
        'stim1_position': stim1_position,
        'stim2_position': stim2_position,
        'break_trial': break_trial,
        'left_text': left_text,
        'right_text': right_text,
        'fixation_time': fixations, # changed from fixed 1.0,
        'instruction_time_min': 2.0,
        'instruction_time_max': 2.0,
        'stim1_time': 1.0,
        'ISI': delays, # changed from fixed 0.8 or 2.0 
        'stim2_time': 1.0,
        'response_instruction_time': 1.0,
        'response_time_max': 3.0,
        'text_holdout_time': 0.3,
        'ITI': 0.0, # removing this, and making it a part of fixation
        'response_time': np.full(n_trials, np.nan), # trial RTs
        'slider_positions': [None] * n_trials,
        'trial_time': np.full(n_trials, np.nan),
        'resp_key': np.full(n_trials, np.nan),
        'complete_flag': 1,
    }
    
    # Get correct responses
    task_struct['correct_responses'] = get_correct_responses(task_struct)

    # Testing the photodiode (for even debug mode or Blackrock off)
    task_struct['photodiode_test_mode'] = True 
    
    # Setting up input devices
    if task_struct['use_cedrus']:
        task_struct['handle'] = init_cedrus()
        task_struct['left_key'] = 4
        task_struct['right_key'] = 5
        task_struct['confirm_key'] = 3
        task_struct['up_key'] = 1
        task_struct['down_key'] = 2
    else:
        task_struct['handle'] = None
        task_struct['left_key'] = 'left'  # Left arrow key
        task_struct['right_key'] = 'right'  # Right arrow key
        task_struct['confirm_key'] = 'space' # Space to submit slider
        task_struct['up_key'] = 'up' # Up arrow key
        task_struct['down_key'] = 'down'  # Down arrow key
    
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
    if screen_size is None:
        win = visual.Window(
            fullscr=full_screen,
            screen=0,
            color=gray,
            units='pix',
            allowGUI=not full_screen
        )
    else:
        win = visual.Window(
            size=screen_size,
            fullscr=full_screen,
            screen=0,
            color=gray,
            units='pix',
            allowGUI=not full_screen
        )
    
    # Getting screen center and dimensions
    # Use window-centered coordinates (origin at 0,0) so stimuli are centered
    center_x = 0
    center_y = 0
    width = win.size[0]
    height = win.size[1]

    dx = width / 5  # originally 12; changed to move stimuli farther apart
    dy = height / 5

    # Size of figures on screen, in pixels (4:3)
    stim_size = 250
    rew_width = 466
    rew_height = 350
    ph = stim_size
    pw = stim_size
    rw = rew_width
    rh = rew_height

    # Setting up stimuli presentation rectangles in centered coordinates
    # vertical_rects: [left, bottom, right, top]
    vertical_rects = [
        [-pw/2, dy - ph/2, pw/2, dy + ph/2],    # top
        [-pw/2, -dy - ph/2, pw/2, -dy + ph/2]   # bottom
    ]

    # horizontal_rects: left, right, center
    horizontal_rects = [
        [-dx - pw/2, -ph/2, -dx + pw/2, ph/2],  # left
        [dx - pw/2, -ph/2, dx + pw/2, ph/2],     # right
        [-rw/2, -rh/2, rw/2, rh/2]               # center
    ]

    # reward_source_rect (kept as pixel box relative to top-left transformed to centered coords)
    reward_source_rect = [-width/2 + 160, -height/2 + 0, -width/2 + 1120, -height/2 + 720]

    # photodiode square
    box_size = height * 0.04
    offset = height * 0.02  # inset margin
    # Bottom-left corner position
    box_x = -width/2 + offset + box_size/2
    box_y = -height/2 + offset + box_size/2
    
    disp_struct['win'] = win
    disp_struct['screen_number'] = 0
    disp_struct['center_x'] = center_x
    disp_struct['center_y'] = center_y
    disp_struct['width'] = width
    disp_struct['height'] = height
    disp_struct['stim_size'] = stim_size
    # disp_struct['rew_width'] = rew_width
    # disp_struct['rew_height'] = rew_height
    # disp_struct['reward_rect'] = horizontal_rects[2]
    # disp_struct['reward_source_rect'] = reward_source_rect
    disp_struct['vertical_rects'] = vertical_rects
    disp_struct['horizontal_rects'] = horizontal_rects
    disp_struct['photodiode_box'] = [box_x, box_y, box_size, box_size]
    disp_struct['photodiode_dur'] = 0.05  # seconds

    image_cache = {}
    for trial_paths in task_struct['trial_stims']:
        for stim_path in trial_paths:  # [stim1_path, stim2_path]
            if stim_path not in image_cache:
                image_cache[stim_path] = visual.ImageStim(
                    win,
                    image=stim_path,
                    units="pix"
                    # don't set size/pos here, we'll set those per trial
                )

    # store in task_struct or local var
    disp_struct['image_cache'] = image_cache
    
    return task_struct, disp_struct



def make_blocks_for_cue(result, cue_value, n_categories, n_response_variants, rng=None):
    """
    For a given cue_value (1 or 2), return two 48-trial blocks
    that are balanced in (category, response_variant).
    """
    if rng is None:
        rng = np.random.default_rng()

    # All indices with this cue
    cue_mask = (result[:, 5] == cue_value)
    idxs = np.where(cue_mask)[0]           # length = 96

    # Extract category and response_variant for those indices
    cats  = result[idxs, 0].astype(int)    # shape (96,)
    resps = result[idxs, 4].astype(int)    # shape (96,)

    # Sort by (category, response_variant): groups become contiguous
    order_within = np.lexsort((resps, cats))   # primary key: cats, secondary: resps
    sorted_idxs_for_cue = idxs[order_within]

    # We know there are 8 (category, resp) combos
    n_combos = n_categories * n_response_variants      # 8
    group_size = len(sorted_idxs_for_cue) // n_combos  # 96 / 8 = 12

    # Reshape to (8 combos, 12 trials per combo)
    grouped = sorted_idxs_for_cue.reshape(n_combos, group_size)  # (8, 12)

    # First half of each row → block A, second half → block B
    half = group_size // 2  # 6
    blockA = grouped[:, :half].ravel()        # (8 * 6,) = (48,)
    blockB = grouped[:, half:2*half].ravel()  # (48,)

    # Shuffle within each block so categories/resp types are intermixed
    blockA = blockA[rng.permutation(blockA.shape[0])]
    blockB = blockB[rng.permutation(blockB.shape[0])]

    return blockA, blockB


def avoid_back_to_back_same_stim(block):
    """
    block: (N, 6) array of trials for ONE block.
    Ensures no two consecutive trials share the same (category, stim_pair)
    (columns 0 and 2). 
    """
    rng = np.random.default_rng()
    
    block = block.copy()
    N = block.shape[0]

    for i in range(1, N):
        # check if current trial has same (category, stim_pair) as previous
        if np.array_equal(block[i, [0, 2]], block[i-1, [0, 2]]):
            curr_pair = block[i-1, [0, 2]]  # (category, stim_pair) we want to avoid
            # find later trials whose (category, stim_pair) differ
            future = block[i+1:, [0, 2]]    # shape (N-i-1, 2)
            mask = np.any(future != curr_pair, axis=1)
            candidates_rel = np.where(mask)[0]

            if candidates_rel.size == 0:
                # no safe swap found; leave as is (very unlikely)
                continue

            # pick a random candidate among the safe ones
            j = i + 1 + rng.choice(candidates_rel)

            # swap i and j
            block[[i, j]] = block[[j, i]]

    return block