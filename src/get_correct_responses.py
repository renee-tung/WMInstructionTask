"""
Given the trial conditions and prompts, get the expected correct response
for each trial in advance (to compare with actual button presses later).
"""

import numpy as np
from pathlib import Path

def get_correct_responses(task_struct):
    """
    Calculate correct responses for all trials.
    
    Parameters:
    -----------
    task_struct : dict
        Task structure containing trial information
    
    Returns:
    --------
    correct_responses : numpy array
        Array of correct response keys (1 or 2) for each trial
    """
    # Getting unique characteristics of each stimulus
    # Note: Paths need to be adjusted based on actual stimulus folder structure
    stims = [
        ['stimuli/Task_Stim_Version2/Animals/Pair1/201.jpg', ['notColorful', 'Multiple']],
        ['stimuli/Task_Stim_Version2/Animals/Pair1/202.jpg', ['Colorful', 'Single']],
        ['stimuli/Task_Stim_Version2/Animals/Pair2/203.jpg', ['Colorful', 'Multiple']],
        ['stimuli/Task_Stim_Version2/Animals/Pair2/204.jpg', ['notColorful', 'Single']],
        ['stimuli/Task_Stim_Version2/Animals/Pair3/205.jpg', ['Colorful', 'Multiple']],
        ['stimuli/Task_Stim_Version2/Animals/Pair3/206.jpg', ['notColorful', 'Single']],
        ['stimuli/Task_Stim_Version2/Animals/Pair4/207.jpg', ['notColorful', 'Multiple']],
        ['stimuli/Task_Stim_Version2/Animals/Pair4/208.jpg', ['Colorful', 'Single']],
        ['stimuli/Task_Stim_Version2/Animals/Pair5/209.jpg', ['Colorful', 'Multiple']],
        ['stimuli/Task_Stim_Version2/Animals/Pair5/210.jpg', ['notColorful', 'Single']],
        ['stimuli/Task_Stim_Version2/Animals/Pair6/212.jpg', ['Colorful', 'Single']],
        ['stimuli/Task_Stim_Version2/Animals/Pair6/211.jpg', ['notColorful', 'Multiple']],
        ['stimuli/Task_Stim_Version2/Cars/Pair1/302.jpg', ['notColorful', 'Old']],
        ['stimuli/Task_Stim_Version2/Cars/Pair1/301.jpg', ['Colorful', 'New']],
        ['stimuli/Task_Stim_Version2/Cars/Pair2/304.jpg', ['Colorful', 'New']],
        ['stimuli/Task_Stim_Version2/Cars/Pair2/303.jpg', ['notColorful', 'Old']],
        ['stimuli/Task_Stim_Version2/Cars/Pair3/306.jpg', ['Colorful', 'New']],
        ['stimuli/Task_Stim_Version2/Cars/Pair3/305.jpg', ['notColorful', 'Old']],
        ['stimuli/Task_Stim_Version2/Cars/Pair4/307.jpg', ['notColorful', 'New']],
        ['stimuli/Task_Stim_Version2/Cars/Pair4/308.jpg', ['Colorful', 'Old']],
        ['stimuli/Task_Stim_Version2/Cars/Pair5/309.jpg', ['notColorful', 'New']],
        ['stimuli/Task_Stim_Version2/Cars/Pair5/310.jpg', ['Colorful', 'Old']],
        ['stimuli/Task_Stim_Version2/Cars/Pair6/311.jpg', ['notColorful', 'New']],
        ['stimuli/Task_Stim_Version2/Cars/Pair6/312.jpg', ['Colorful', 'Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair1/101.jpg', ['Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair1/102.jpg', ['New']],
        ['stimuli/Task_Stim_Version2/Faces/Pair2/103.jpg', ['New']],
        ['stimuli/Task_Stim_Version2/Faces/Pair2/104.jpg', ['Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair3/105.jpg', ['New']],
        ['stimuli/Task_Stim_Version2/Faces/Pair3/106.jpg', ['Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair4/107.jpg', ['New']],
        ['stimuli/Task_Stim_Version2/Faces/Pair4/108.jpg', ['Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair5/110.jpg', ['Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair5/109.jpg', ['New']],
        ['stimuli/Task_Stim_Version2/Faces/Pair6/111.jpg', ['Old']],
        ['stimuli/Task_Stim_Version2/Faces/Pair6/112.jpg', ['New']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair1/401.jpg', ['Multiple']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair1/402.jpg', ['Single']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair2/404.jpg', ['Single']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair2/403.jpg', ['Multiple']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair3/405.jpg', ['Multiple']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair3/406.jpg', ['Single']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair4/407.jpg', ['Single']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair4/408.jpg', ['Multiple']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair5/409.jpg', ['Single']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair5/410.jpg', ['Multiple']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair6/411.jpg', ['Multiple']],
        ['stimuli/Task_Stim_Version2/Fruits/Pair6/412.jpg', ['Single']],
    ]
    
    n_trials = task_struct['n_trials']
    correct_responses = np.full(n_trials, np.nan)
    trial_variant = np.array(task_struct['anti_task']) + np.array(task_struct['prompt_variant'])
    
    for t_i in range(n_trials):
        axis = task_struct['trial_axis'][t_i]
        category = task_struct['trial_categories'][t_i]
        trial_axis_name = task_struct['category_and_axis'][1][category][axis]
        
        # Determine target feature based on trial axis and variant
        if trial_axis_name == 'Colorful':
            target_feature = 'notColorful'
            if trial_variant[t_i] == 1:
                target_feature = 'Colorful'
        elif trial_axis_name == 'Count':
            target_feature = 'Single'
            if trial_variant[t_i] == 1:
                target_feature = 'Multiple'
        elif trial_axis_name == 'Identical':
            target_feature = ''
        elif trial_axis_name == 'New':
            target_feature = 'Old'
            if trial_variant[t_i] == 1:
                target_feature = 'New'
        else:
            target_feature = ''
        
        trial_text = [task_struct['left_text'][t_i], task_struct['right_text'][t_i]]
        
        if trial_axis_name == 'Identical':
            # Check if stimuli are identical
            stim1_path = task_struct['trial_stims'][t_i][0]
            stim2_path = task_struct['trial_stims'][t_i][1]
            if stim1_path == stim2_path:
                # Correct response = yes (in task) / no (antitask)
                if not task_struct['anti_task'][t_i]:
                    correct_key = [i for i, text in enumerate(trial_text, 1) if 'Yes' in text][0]
                else:
                    correct_key = [i for i, text in enumerate(trial_text, 1) if 'No' in text][0]
            else:
                # Correct response = no (in task) / yes (anti task)
                if not task_struct['anti_task'][t_i]:
                    correct_key = [i for i, text in enumerate(trial_text, 1) if 'No' in text][0]
                else:
                    correct_key = [i for i, text in enumerate(trial_text, 1) if 'Yes' in text][0]
        else:
            # Other conditions than identical
            stim1_path = task_struct['trial_stims'][t_i][0]
            stim2_path = task_struct['trial_stims'][t_i][1]
            
            # Find stimulus indices
            stim1_idx = None
            stim2_idx = None
            for i, (stim_path, _) in enumerate(stims):
                if stim_path in stim1_path or Path(stim1_path).name in stim_path:
                    stim1_idx = i
                if stim_path in stim2_path or Path(stim2_path).name in stim_path:
                    stim2_idx = i
            
            if stim1_idx is None or stim2_idx is None:
                continue
            
            stim_features = [stims[stim1_idx][1], stims[stim2_idx][1]]
            # Check which stimulus has the target feature (1 = first, 2 = second)
            stim_with_target_feature = 2 if target_feature in stim_features[1] else 1
            
            if stim_with_target_feature == 1:
                correct_key = [i for i, text in enumerate(trial_text, 1) if 'First' in text][0]
            else:
                correct_key = [i for i, text in enumerate(trial_text, 1) if 'Second' in text][0]
        
        correct_responses[t_i] = correct_key
    
    return correct_responses

