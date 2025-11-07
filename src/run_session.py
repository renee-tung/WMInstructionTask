"""
This function runs a general verbal instruction task session, given a
set of task parameters and inputs.
"""

import numpy as np
from psychopy import visual, event, core
from pathlib import Path
import pickle

from send_ttl import send_ttl
from set_marker_ids import *
from intermission_screen import intermission_screen
from get_instruction_text import get_instruction_text

def run_session(task_struct, disp_struct):
    """
    Run the experimental session.
    
    Parameters:
    -----------
    task_struct : dict
        Task structure containing all trial parameters
    disp_struct : dict
        Display structure containing window and layout information
    
    Returns:
    --------
    task_struct : dict
        Updated task structure
    disp_struct : dict
        Updated display structure
    """
    # Making sure event buffer is empty
    event.clearEvents()
    
    # Looping over trials
    trial_struct_cell = [None] * task_struct['n_trials']
    win = disp_struct['win']
    width = disp_struct['width']
    height = disp_struct['height']
    
    for t_i in range(task_struct['n_trials']):
        if t_i == 0:
            intermission_screen('Wait for start!', task_struct, disp_struct)
        
        trial_start_time = core.getTime()
        
        # Displaying message on console
        print(f'Trial number {t_i + 1} / {task_struct["n_trials"]}')
        
        # Checking whether we want to interrupt or pause the experiment
        keys = event.getKeys()
        if keys:
            # Check if the experimenter is pressing a key
            if task_struct['escape_key'] in keys:
                # Experiment incomplete upon finishing
                task_struct['complete_flag'] = 0
                from finish_experiment import finish_experiment
                finish_experiment(task_struct, disp_struct)
                return task_struct, disp_struct
            
            # Checking if we want to just pause the experiment
            if task_struct['pause_key'] in keys:
                event.clearEvents()
                while True:
                    keys = event.waitKeys(keyList=[task_struct['continue_key']])
                    if keys:
                        break
        
        # Creating trial struct
        trial_struct = {}
        
        # Presenting fixation cross
        win.flip()  # Clearing screen
        fixation_line1 = visual.Line(
            win,
            start=[width/2, height/2 - 20],
            end=[width/2, height/2 + 20],
            lineColor='black',
            lineWidth=5
        )
        fixation_line2 = visual.Line(
            win,
            start=[width/2 - 20, height/2],
            end=[width/2 + 20, height/2],
            lineColor='black',
            lineWidth=5
        )
        fixation_line1.draw()
        fixation_line2.draw()
        trial_struct['fixation1_flip'] = win.flip()
        core.wait(task_struct['fixation_time'])
        
        # Presenting first instruction (if required)
        if task_struct['trial_conditions'][t_i] == 1:
            plotted_text = get_instruction_text_for_trial(task_struct, t_i)
            # Cleaning screen
            win.flip()
            instruction_text = visual.TextStim(
                win,
                text=plotted_text,
                color='white',
                height=48,
                wrapWidth=win.size[0] * 0.8
            )
            instruction_text.draw()
            trial_struct['instruction1_flip'] = win.flip()
            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'INSTRUCTION_ON', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'INSTRUCTION_ON')
            
            # Wait for at least this amount of time
            core.wait(task_struct['instruction_time_min'])
            
            # Wait more for key press or continue after another set interval
            event.clearEvents()
            keys = event.waitKeys(
                keyList=['space'],
                maxWait=task_struct['instruction_time_max'] - task_struct['instruction_time_min'],
                timeStamped=True
            )
            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'INSTRUCTION_OFF', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'INSTRUCTION_OFF')
        
        # Presenting first stimulus
        stim1_position_trial = int(task_struct['stim1_position'][t_i])
        stim1_rect = disp_struct['horizontal_rects'][stim1_position_trial - 1]
        
        # Load and display image
        stim1_path = task_struct['trial_stims'][t_i][0]
        stim1_image = visual.ImageStim(
            win,
            image=stim1_path,
            pos=None,
            size=(stim1_rect[2] - stim1_rect[0], stim1_rect[3] - stim1_rect[1])
        )
        stim1_image.setPos((stim1_rect[0] + stim1_rect[2])/2, (stim1_rect[1] + stim1_rect[3])/2)
        stim1_image.draw()
        
        trial_struct['stim1_flip'] = win.flip()
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
            # Eyelink message would go here
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_ON')
        
        # Wait for stimulus presentation
        core.wait(task_struct['stim1_time'])
        
        # Sending stim off message before instruction/stim2
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_OFF', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_OFF')
        
        trial_struct['stim1_off_flip'] = win.flip()
        # Wait for inter-stimulus interval
        core.wait(task_struct['ISI']) # want to double check what's on the screen here
        
        
        # Presenting second stimulus
        stim2_position_trial = int(task_struct['stim2_position'][t_i])
        stim2_rect = disp_struct['horizontal_rects'][stim2_position_trial - 1]
        
        # Load and display image
        stim2_path = task_struct['trial_stims'][t_i][1]
        stim2_image = visual.ImageStim(
            win,
            image=stim2_path,
            pos=None,
            size=(stim2_rect[2] - stim2_rect[0], stim2_rect[3] - stim2_rect[1])
        )
        stim2_image.setPos((stim2_rect[0] + stim2_rect[2])/2, (stim2_rect[1] + stim2_rect[3])/2)
        stim2_image.draw()
        
        trial_struct['stim2_flip'] = win.flip()
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_ON')
        
        # Wait for stimulus presentation
        core.wait(task_struct['stim2_time'])
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_OFF', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_OFF')

        # Presenting second instruction (if required)
        if task_struct['trial_conditions'][t_i] == 2:
            plotted_text = get_instruction_text_for_trial(task_struct, t_i)
            # Cleaning screen
            win.flip()
            instruction_text = visual.TextStim(
                win,
                text=plotted_text,
                color='white',
                height=48,
                wrapWidth=win.size[0] * 0.8
            )
            instruction_text.draw()
            trial_struct['instruction2_flip'] = win.flip()
            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'INSTRUCTION_ON', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'INSTRUCTION_ON')
            
            # Wait for at least this amount of time
            core.wait(task_struct['instruction_time_min'])
            
            # Wait more for key press or continue after another set interval
            event.clearEvents()
            keys = event.waitKeys(
                keyList=['space'],
                maxWait=task_struct['instruction_time_max'] - task_struct['instruction_time_min'],
                timeStamped=True
            )
            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'INSTRUCTION_OFF', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'INSTRUCTION_OFF')
        
        # Getting response
        # Plotting left/right frames
        left_rect = [x + offset for x, offset in zip(disp_struct['horizontal_rects'][0], [-10, -10, 10, 10])]
        right_rect = [x + offset for x, offset in zip(disp_struct['horizontal_rects'][1], [-10, -10, 10, 10])]
        
        left_frame = visual.Rect(
            win,
            width=left_rect[2] - left_rect[0],
            height=left_rect[3] - left_rect[1],
            pos=((left_rect[0] + left_rect[2])/2, (left_rect[1] + left_rect[3])/2),
            lineColor='green',
            fillColor=None,
            lineWidth=5
        )
        right_frame = visual.Rect(
            win,
            width=right_rect[2] - right_rect[0],
            height=right_rect[3] - right_rect[1],
            pos=((right_rect[0] + right_rect[2])/2, (right_rect[1] + right_rect[3])/2),
            lineColor='red',
            fillColor=None,
            lineWidth=5
        )
        
        left_text_stim = visual.TextStim(
            win,
            text=task_struct['left_text'][t_i],
            color='white',
            height=48,
            pos=((disp_struct['horizontal_rects'][0][0] + disp_struct['horizontal_rects'][0][2])/2,
                 (disp_struct['horizontal_rects'][0][1] + disp_struct['horizontal_rects'][0][3])/2)
        )
        right_text_stim = visual.TextStim(
            win,
            text=task_struct['right_text'][t_i],
            color='white',
            height=48,
            pos=((disp_struct['horizontal_rects'][1][0] + disp_struct['horizontal_rects'][1][2])/2,
                 (disp_struct['horizontal_rects'][1][1] + disp_struct['horizontal_rects'][1][3])/2)
        )
        
        left_frame.draw()
        right_frame.draw()
        left_text_stim.draw()
        right_text_stim.draw()
        
        trial_struct['stim_response_prompt_flip'] = win.flip()
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_ON')
        
        # Redraw for next flip
        left_frame.draw()
        right_frame.draw()
        left_text_stim.draw()
        right_text_stim.draw()
        
        # Wait for subject's response
        cue_time = core.getTime()
        current_time = cue_time
        response_received = False
        
        # CEDRUS button box code commented out - using keyboard only
        # if task_struct['use_cedrus']:
        #     # CEDRUS response box handling
        #     handle = task_struct['handle']
        #     if handle:
        #         # Clear buffer
        #         handle.reset_input_buffer()
        #     
        #     while current_time - cue_time < task_struct['response_time_max']:
        #         if handle:
        #             # Check CEDRUS button box
        #             # Note: Actual implementation depends on CEDRUS API
        #             # This is a placeholder
        #             try:
        #                 if handle.in_waiting > 0:
        #                     data = handle.read(handle.in_waiting)
        #                     # Parse CEDRUS response (button codes vary by device)
        #                     # Placeholder: assuming button 4 = left, button 5 = right
        #             except:
        #                 pass
        #         
        #         # Also check keyboard as backup
        #         keys = event.getKeys(keyList=[task_struct['left_key'], task_struct['right_key']], timeStamped=True)
        #         if keys:
        #             key, time = keys[0]
        #             task_struct['response_time'][t_i] = time - cue_time
        #             if key == task_struct['left_key']:
        #                 task_struct['resp_key'][t_i] = 1
        #                 if task_struct['eye_link_mode']:
        #                     write_log_with_eyelink(task_struct, 'RESPONSE_LEFT', '')
        #                 if not task_struct['debug']:
        #                     send_ttl(task_struct, 'RESPONSE_LEFT')
        #                 # Plotting grayed out selected text
        #                 left_text_stim.color = 'gray'
        #                 left_text_stim.draw()
        #                 left_frame.draw()
        #                 right_frame.draw()
        #                 right_text_stim.draw()
        #                 trial_struct['button_press_flip'] = win.flip()
        #                 core.wait(task_struct['text_holdout_time'])
        #                 response_received = True
        #                 break
        #             elif key == task_struct['right_key']:
        #                 task_struct['resp_key'][t_i] = 2
        #                 if task_struct['eye_link_mode']:
        #                     write_log_with_eyelink(task_struct, 'RESPONSE_RIGHT', '')
        #                 if not task_struct['debug']:
        #                     send_ttl(task_struct, 'RESPONSE_RIGHT')
        #                 # Plotting grayed out selected text
        #                 right_text_stim.color = 'gray'
        #                 left_frame.draw()
        #                 right_frame.draw()
        #                 left_text_stim.draw()
        #                 right_text_stim.draw()
        #                 trial_struct['button_press_flip'] = win.flip()
        #                 core.wait(task_struct['text_holdout_time'])
        #                 response_received = True
        #                 break
        #         
        #         current_time = core.getTime()
        # else:
        # Keyboard response (using arrow keys)
        event.clearEvents()
        while current_time - cue_time < task_struct['response_time_max']:
            keys = event.getKeys(keyList=[task_struct['left_key'], task_struct['right_key']], timeStamped=True)
            if keys:
                key, time = keys[0]
                task_struct['response_time'][t_i] = time - cue_time
                if key == task_struct['left_key']:
                    task_struct['resp_key'][t_i] = 1
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'RESPONSE_LEFT', '')
                    if not task_struct['debug']:
                        send_ttl(task_struct, 'RESPONSE_LEFT')
                    # Plotting grayed out selected text
                    left_text_stim.color = 'gray'
                    left_text_stim.draw()
                    left_frame.draw()
                    right_frame.draw()
                    right_text_stim.draw()
                    trial_struct['button_press_flip'] = win.flip()
                    core.wait(task_struct['text_holdout_time'])
                    response_received = True
                    break
                elif key == task_struct['right_key']:
                    task_struct['resp_key'][t_i] = 2
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'RESPONSE_RIGHT', '')
                    if not task_struct['debug']:
                        send_ttl(task_struct, 'RESPONSE_RIGHT')
                    # Plotting grayed out selected text
                    right_text_stim.color = 'gray'
                    left_frame.draw()
                    right_frame.draw()
                    left_text_stim.draw()
                    right_text_stim.draw()
                    trial_struct['button_press_flip'] = win.flip()
                    core.wait(task_struct['text_holdout_time'])
                    response_received = True
                    break
            
            current_time = core.getTime()
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_OFF', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_OFF')
        
        trial_struct['response_end_flip'] = win.flip()
        # Wait for intertrial interval
        core.wait(task_struct['ITI'])
        
        # Saving trial to struct
        trial_struct_cell[t_i] = trial_struct
        task_struct['trial_struct_cell'] = trial_struct_cell  # Save full array, not just current trial
        
        trial_end_time = core.getTime()
        task_struct['trial_time'][t_i] = trial_end_time - trial_start_time
        
        # Saving to file after every trial
        output_file = task_struct['output_folder'] / task_struct['file_name']
        with open(output_file.with_suffix('.pkl'), 'ab') as f:
            pickle.dump({'task_struct': task_struct}, f)
        
        # End of block message on screen (including accuracy in the previous block)
        if task_struct['break_trial'][t_i]:
            block_trials = list(range(max(0, t_i - task_struct['n_trials_per_block'] + 1), t_i + 1))
            correct = np.array(task_struct['correct_responses'])[block_trials]
            resp = np.array(task_struct['resp_key'])[block_trials]
            block_accuracy = 100 * np.nansum(correct == resp) / task_struct['n_trials_per_block']
            intermission_screen(
                f'Break time! \n Your accuracy was {block_accuracy:.1f}%',
                task_struct, disp_struct
            )
    
    return task_struct, disp_struct


def get_instruction_text_for_trial(task_struct, t_i):
    """Helper function to get instruction text for a trial."""
    category = task_struct['trial_categories'][t_i]
    axis = task_struct['trial_axis'][t_i]
    trial_axis_name = task_struct['category_and_axis'][1][category][axis]
    return get_instruction_text(
        category, trial_axis_name,
        task_struct['anti_task'][t_i],
        task_struct['prompt_variant'][t_i],
        task_struct['equivalent_variant_id'][t_i]
    )


def write_log_with_eyelink(task_struct, event_name, message):
    """Write log entry with EyeLink."""
    if 'fid_log' in task_struct and task_struct['fid_log']:
        import time
        timestamp = time.time()
        log_entry = f"{timestamp}\t{event_name}\t{message}\n"
        task_struct['fid_log'].write(log_entry)
        task_struct['fid_log'].flush()

