"""
This function runs a general verbal instruction task session, given a
set of task parameters and inputs.
"""

from calendar import c
from os import times
from turtle import left
import numpy as np
from psychopy import visual, event, core
from psychopy.hardware import keyboard
from pathlib import Path
import pickle
import pdb

from src.send_ttl import send_ttl
from src.set_marker_ids import *
from src.intermission_screen import intermission_screen
from src.get_instruction_text import get_instruction_text
from src.get_motor_instruction_text import get_motor_instruction_text
from src.finish_experiment import finish_experiment

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

    # Pre-create slider (used only on slider trials)
    divider_line = visual.Line(win=win, name='divider_line',
                                units='norm', start=(0, -0.2), end=(0,  0.2), 
                                lineWidth=3.0, lineColor=[1.0, 1.0, 1.0])

    slider_line = visual.Line(win=win, name='slider_line',
                              units='norm', start=(-0.5, 0.0), end=( 0.5, 0.0),
                              lineWidth=5.0, lineColor=[-1.0, -1.0, -1.0])

    marker = visual.Slider(win=win, name='marker',
                           units='norm', pos=(0.0, 0.0),
                           size=(0.8, 0.08), # 80% of width, 8% of height
                           labels=None, ticks=(-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5),
                           granularity=0.001, style='slider', styleTweaks=('labels45',),
                           opacity=1.0, markerColor=[-1.0, -1.0, -1.0],
                           lineColor=None, labelHeight=0.05, readOnly=False)
    
    for t_i in range(task_struct['n_trials']):
        if t_i == 0:
            intermission_screen('Wait for start!', task_struct, disp_struct)
        
        trial_start_time = core.getTime()
        
        # Displaying message on console
        print(f'Trial number {t_i + 1} / {task_struct["n_trials"]}')
        
        # Creating trial struct
        trial_struct = {}
        
        # Presenting fixation cross
        win.flip()  # Clearing screen
        fixation_line1 = visual.Line(
            win,
            start=[0, -20],
            end=[0, 20],
            lineColor='black',
            lineWidth=5
        )
        fixation_line2 = visual.Line(
            win,
            start=[-20, 0],
            end=[20, 0],
            lineColor='black',
            lineWidth=5
        )
        fixation_line1.draw()
        fixation_line2.draw()
        trial_struct['fixation1_flip'] = win.flip()
        core.wait(task_struct['fixation_time'][t_i])
        
        # Check control keys (escape/pause) using helper
        res = check_for_control_keys(task_struct, disp_struct)
        
        # Presenting pre-stim instruction (if required)
        if task_struct['trial_conditions'][t_i] == 1:
            plotted_text = get_instruction_text_for_trial(task_struct, t_i)
            # Cleaning screen
            instruction_onset = win.flip()
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
            if keys:
                key, key_time = keys[0]
                instruction_end_time = key_time
            else:
                # no keypress, use max time
                instruction_end_time = core.getTime()
            task_struct['instruction_time'][t_i] = instruction_end_time - instruction_onset
            
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

        stim1_image.setPos(((stim1_rect[0] + stim1_rect[2]) / 2, (stim1_rect[1] + stim1_rect[3]) / 2,))
        stim1_image.draw()
        
        trial_struct['stim1_flip'] = win.flip()
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
            # Eyelink message would go here
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_ON')
        
        # Wait for stimulus presentation
        core.wait(task_struct['stim1_time'])
        
        # Sending stim off message before stim2
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'STIMULUS_OFF', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'STIMULUS_OFF')
        
        trial_struct['stim1_off_flip'] = win.flip()

        # Wait for inter-stimulus interval (with fixation cross)
        win.flip()  # Clearing screen
        fixation_line1 = visual.Line(
            win,
            start=[0, -20],
            end=[0, 20],
            lineColor='black',
            lineWidth=5
        )
        fixation_line2 = visual.Line(
            win,
            start=[-20, 0],
            end=[20, 0],
            lineColor='black',
            lineWidth=5
        )
        fixation_line1.draw()
        fixation_line2.draw()
        trial_struct['fixation1_flip'] = win.flip()
        core.wait(task_struct['ISI'][t_i])
        
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
        stim2_image.setPos(((stim2_rect[0] + stim2_rect[2])/2, (stim2_rect[1] + stim2_rect[3])/2))
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

        # Presenting retrocue instruction (if required)
        if task_struct['trial_conditions'][t_i] == 2:
            plotted_text = get_instruction_text_for_trial(task_struct, t_i)
            # Cleaning screen
            instruction_onset = win.flip()
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
            if keys:
                key, key_time = keys[0]
                instruction_end_time = key_time
            else:
                instruction_end_time = core.getTime()
            task_struct['instruction_time'][t_i] = instruction_end_time - instruction_onset
            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'INSTRUCTION_OFF', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'INSTRUCTION_OFF')

        # Presenting response instruction (button or slider)
        plotted_text = get_motor_instruction_text_for_trial(task_struct, t_i)
        # Cleaning screen
        instruction_onset = win.flip()
        instruction_text = visual.TextStim(
            win,
            text=plotted_text,
            color='white',
            height=48,
            wrapWidth=win.size[0] * 0.8
        )
        instruction_text.draw()
        trial_struct['responseinstruction_flip'] = win.flip()
        
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'INSTRUCTION_ON', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'INSTRUCTION_ON')
        
        # Wait for at least this amount of time
        core.wait(task_struct['response_instruction_time'])
                
        if task_struct['eye_link_mode']:
            write_log_with_eyelink(task_struct, 'INSTRUCTION_OFF', '')
        
        if not task_struct['debug']:
            send_ttl(task_struct, 'INSTRUCTION_OFF')
        

        # Getting response
        if task_struct['response_variant'][t_i] == 1: # slider response
            
            # Display words above the endpoints of the slider
            left_text_stim = visual.TextStim(win, text=task_struct['left_text'][t_i],
                                             color='white', units='norm', 
                                             height=0.08, pos=(-0.4, 0.25))   # left/top

            right_text_stim = visual.TextStim(win, text=task_struct['right_text'][t_i],
                                              color='white', units='norm',
                                              height=0.08, pos=(0.4, 0.25))    # right/top
            
            reminder_text = visual.TextStim(win, text="Press UP to confirm your answer",
                                            color='white', units='norm', 
                                            height=0.05, pos=(0, -0.25))
            
            # left_pressed, right_pressed, marker_moved = 0, 0, 0
            positions = []
            times = []

            marker_move = 0.1 # amount to move marker per key press

            event.clearEvents()

            divider_line.setPos([0, 0])
            marker.reset()
            marker.markerPos = 0.0  # Start in middle
            slider_resp = keyboard.Keyboard()

            # store start times
            cue_time = core.getTime()
            current_time = cue_time
            response_received = False

            # Set up Cedrus if used
            handle = None
            if task_struct['use_cedrus']:
                handle = task_struct.get('handle', None)
                if handle:
                    handle.reset_input_buffer()

            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'STIMULUS_ON')

            while current_time - cue_time < task_struct['response_time_max']:
                
                # Draw existing response frame
                left_text_stim.draw()
                right_text_stim.draw()

                # Draw slider
                marker.draw()
                divider_line.draw()
                slider_line.draw()
                win.flip()

                # Show reminder if enough time passed without confirmation
                if (current_time - cue_time) > 2:
                    reminder_text.draw()

                # Check for slider movement
                keys = slider_resp.getKeys(keyList=['left','right','up'], waitRelease=False, clear=False)
                key_names = [k.name for k in keys]
                if 'left' in key_names:
                    # move left
                    if (-0.5 + marker_move) <= marker.markerPos:
                        marker.markerPos -= marker_move
                if 'right' in key_names:
                    # move right
                    if (0.5 - marker_move) >= marker.markerPos:
                        marker.markerPos += marker_move

                positions.append(marker.markerPos)
                times.append(current_time - cue_time)
                
                if 'up' in key_names:
                    # submit
                    rating = marker.markerPos
                    rt = core.getTime() - cue_time
                    
                    # Store response
                    if rating < 0:
                        task_struct['resp_key'][t_i] = 1
                        if task_struct['eye_link_mode']:
                            write_log_with_eyelink(task_struct, f"RESPONSE_LEFT", "")
                        if not task_struct['debug']:
                            send_ttl(task_struct, "RESPONSE_LEFT")
                        left_text_stim.color = 'gray'
                        left_text_stim.draw()
                        right_text_stim.draw()
                        marker.draw()
                        divider_line.draw()
                        slider_line.draw()
                        trial_struct['button_press_flip'] = win.flip()
                        core.wait(task_struct['text_holdout_time'])
                        response_received = True
                    elif rating > 0: 
                        task_struct['resp_key'][t_i] = 2
                        if task_struct['eye_link_mode']:
                            write_log_with_eyelink(task_struct, f"RESPONSE_RIGHT", "")
                        if not task_struct['debug']:
                            send_ttl(task_struct, "RESPONSE_RIGHT")
                        right_text_stim.color = 'gray'
                        left_text_stim.draw()
                        right_text_stim.draw()
                        marker.draw()
                        divider_line.draw()
                        slider_line.draw()
                        trial_struct['button_press_flip'] = win.flip()
                        core.wait(task_struct['text_holdout_time'])
                        response_received = True
                    
                    task_struct['response_time'][t_i] = rt

                    # store marker positions for analysis
                    task_struct['slider_positions'][t_i] = {
                        'pos': np.array(positions), 
                        'time': np.array(times)}

                    break

                current_time = core.getTime()
            
            if not response_received: # no response recorded, store NaNs
                task_struct['resp_key'][t_i] = np.nan
                task_struct['response_time'][t_i] = np.nan
                task_struct['slider_positions'][t_i] = {
                    'pos': np.array(positions), 
                    'time': np.array(times)}

        else: # Button response

            # Plotting top/bottom frames (changed from left/right)
            top_rect = [x + offset for x, offset in zip(disp_struct['vertical_rects'][0], [-10, -10, 10, 10])]
            bottom_rect = [x + offset for x, offset in zip(disp_struct['vertical_rects'][1], [-10, -10, 10, 10])]

            top_frame = visual.Rect(
                win,
                width=top_rect[2] - top_rect[0],
                height=top_rect[3] - top_rect[1],
                pos=((top_rect[0] + top_rect[2])/2, (top_rect[1] + top_rect[3])/2),
                lineColor='green',
                fillColor=None,
                lineWidth=5
            )
            bottom_frame = visual.Rect(
                win,
                width=bottom_rect[2] - bottom_rect[0],
                height=bottom_rect[3] - bottom_rect[1],
                pos=((bottom_rect[0] + bottom_rect[2])/2, (bottom_rect[1] + bottom_rect[3])/2),
                lineColor='red',
                fillColor=None,
                lineWidth=5
            )

            top_text_stim = visual.TextStim(
                win,
                text=task_struct['left_text'][t_i],
                color='white',
                height=48,
                pos=((disp_struct['vertical_rects'][0][0] + disp_struct['vertical_rects'][0][2])/2,
                    (disp_struct['vertical_rects'][0][1] + disp_struct['vertical_rects'][0][3])/2)
            )
            bottom_text_stim = visual.TextStim(
                win,
                text=task_struct['right_text'][t_i],
                color='white',
                height=48,
                pos=((disp_struct['vertical_rects'][1][0] + disp_struct['vertical_rects'][1][2])/2,
                    (disp_struct['vertical_rects'][1][1] + disp_struct['vertical_rects'][1][3])/2)
            )
            
            top_frame.draw()
            bottom_frame.draw()
            top_text_stim.draw()
            bottom_text_stim.draw()
            
            trial_struct['stim_response_prompt_flip'] = win.flip()
            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
            
            if not task_struct['debug']:
                send_ttl(task_struct, 'STIMULUS_ON')
            
            # Redraw for next flip
            top_frame.draw()
            bottom_frame.draw()
            top_text_stim.draw()
            bottom_text_stim.draw()
            
            # Wait for subject's response
            cue_time = core.getTime()
            current_time = cue_time
            response_received = False

            if task_struct['use_cedrus']:
                # CEDRUS response box handling
                handle = task_struct['handle']
                if handle:
                    # Clear buffer
                    handle.reset_input_buffer()
                
                while current_time - cue_time < task_struct['response_time_max']:
                    
                    if handle:
                        # Check CEDRUS button box
                        # Note: Actual implementation depends on CEDRUS API
                        # This is a placeholder
                        try:
                            if handle.in_waiting > 0:
                                data = handle.read(handle.in_waiting)
                                # Parse CEDRUS response (button codes vary by device)
                                # Placeholder: assuming button 4 = left, button 5 = right
                        except:
                            pass
                    
                    # Also check keyboard as backup
                    keys = event.getKeys(keyList=[task_struct['up_key'], task_struct['down_key']], timeStamped=True)
                    if keys:
                        key, time = keys[0]
                        task_struct['response_time'][t_i] = time - cue_time
                        if key == task_struct['up_key']:
                            task_struct['resp_key'][t_i] = 1
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, 'RESPONSE_LEFT', '')
                            if not task_struct['debug']:
                                send_ttl(task_struct, 'RESPONSE_LEFT')
                            # Plotting grayed out selected text
                            top_text_stim.color = 'gray'
                            top_text_stim.draw()
                            top_frame.draw()
                            bottom_frame.draw()
                            bottom_text_stim.draw()
                            trial_struct['button_press_flip'] = win.flip()
                            core.wait(task_struct['text_holdout_time'])
                            response_received = True
                            break
                        elif key == task_struct['down_key']:
                            task_struct['resp_key'][t_i] = 2
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, 'RESPONSE_RIGHT', '')
                            if not task_struct['debug']:
                                send_ttl(task_struct, 'RESPONSE_RIGHT')
                            # Plotting grayed out selected text
                            bottom_text_stim.color = 'gray'
                            top_frame.draw()
                            bottom_frame.draw()
                            top_text_stim.draw()
                            bottom_text_stim.draw()
                            trial_struct['button_press_flip'] = win.flip()
                            core.wait(task_struct['text_holdout_time'])
                            response_received = True
                            break
                    
                    current_time = core.getTime()
            else:
                # Keyboard response (using arrow keys)
                event.clearEvents()
                while current_time - cue_time < task_struct['response_time_max']:
                    
                    keys = event.getKeys(keyList=[task_struct['up_key'], task_struct['down_key']], timeStamped=True)
                    if keys:
                        key, time = keys[0]
                        task_struct['response_time'][t_i] = time - cue_time
                        if key == task_struct['up_key']:
                            task_struct['resp_key'][t_i] = 1
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, 'RESPONSE_UP', '')
                            if not task_struct['debug']:
                                send_ttl(task_struct, 'RESPONSE_UP')
                            # Plotting grayed out selected text
                            top_text_stim.color = 'gray'
                            top_text_stim.draw()
                            top_frame.draw()
                            bottom_frame.draw()
                            bottom_text_stim.draw()
                            trial_struct['button_press_flip'] = win.flip()
                            core.wait(task_struct['text_holdout_time'])
                            response_received = True
                            break
                        elif key == task_struct['down_key']:
                            task_struct['resp_key'][t_i] = 2
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, 'RESPONSE_DOWN', '')
                            if not task_struct['debug']:
                                send_ttl(task_struct, 'RESPONSE_DOWN')
                            # Plotting grayed out selected text
                            bottom_text_stim.color = 'gray'
                            top_frame.draw()
                            bottom_frame.draw()
                            top_text_stim.draw()
                            bottom_text_stim.draw()
                            trial_struct['button_press_flip'] = win.flip()
                            core.wait(task_struct['text_holdout_time'])
                            response_received = True
                            break
                    
                    current_time = core.getTime()
        

            # # Plotting left/right frames
            # left_rect = [x + offset for x, offset in zip(disp_struct['horizontal_rects'][0], [-10, -10, 10, 10])]
            # right_rect = [x + offset for x, offset in zip(disp_struct['horizontal_rects'][1], [-10, -10, 10, 10])]
            
            # left_frame = visual.Rect(
            #     win,
            #     width=left_rect[2] - left_rect[0],
            #     height=left_rect[3] - left_rect[1],
            #     pos=((left_rect[0] + left_rect[2])/2, (left_rect[1] + left_rect[3])/2),
            #     lineColor='green',
            #     fillColor=None,
            #     lineWidth=5
            # )
            # right_frame = visual.Rect(
            #     win,
            #     width=right_rect[2] - right_rect[0],
            #     height=right_rect[3] - right_rect[1],
            #     pos=((right_rect[0] + right_rect[2])/2, (right_rect[1] + right_rect[3])/2),
            #     lineColor='red',
            #     fillColor=None,
            #     lineWidth=5
            # )
            
            # left_text_stim = visual.TextStim(
            #     win,
            #     text=task_struct['left_text'][t_i],
            #     color='white',
            #     height=48,
            #     pos=((disp_struct['horizontal_rects'][0][0] + disp_struct['horizontal_rects'][0][2])/2,
            #         (disp_struct['horizontal_rects'][0][1] + disp_struct['horizontal_rects'][0][3])/2)
            # )
            # right_text_stim = visual.TextStim(
            #     win,
            #     text=task_struct['right_text'][t_i],
            #     color='white',
            #     height=48,
            #     pos=((disp_struct['horizontal_rects'][1][0] + disp_struct['horizontal_rects'][1][2])/2,
            #         (disp_struct['horizontal_rects'][1][1] + disp_struct['horizontal_rects'][1][3])/2)
            # )
            
            # left_frame.draw()
            # right_frame.draw()
            # left_text_stim.draw()
            # right_text_stim.draw()
            
            # trial_struct['stim_response_prompt_flip'] = win.flip()
            
            # if task_struct['eye_link_mode']:
            #     write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')
            
            # if not task_struct['debug']:
            #     send_ttl(task_struct, 'STIMULUS_ON')
            
            # # Redraw for next flip
            # left_frame.draw()
            # right_frame.draw()
            # left_text_stim.draw()
            # right_text_stim.draw()
            
            # # Wait for subject's response
            # cue_time = core.getTime()
            # current_time = cue_time
            # response_received = False

            # if task_struct['use_cedrus']:
            #     # CEDRUS response box handling
            #     handle = task_struct['handle']
            #     if handle:
            #         # Clear buffer
            #         handle.reset_input_buffer()
                
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
                    
            #         current_time = core.getTime()
            # else:
            #     # Keyboard response (using arrow keys)
            #     event.clearEvents()
            #     while current_time - cue_time < task_struct['response_time_max']:
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
                    
            #         current_time = core.getTime()
        
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


def get_motor_instruction_text_for_trial(task_struct, t_i):
    """Helper function to get motor instruction text for a trial. """
    response_variant = task_struct['response_variant']
    return get_motor_instruction_text(response_variant[t_i])


def write_log_with_eyelink(task_struct, event_name, message):
    """Write log entry with EyeLink."""
    if 'fid_log' in task_struct and task_struct['fid_log']:
        import time
        timestamp = time.time()
        log_entry = f"{timestamp}\t{event_name}\t{message}\n"
        task_struct['fid_log'].write(log_entry)
        task_struct['fid_log'].flush()

def check_for_control_keys(task_struct, disp_struct):
    """
    Check for experimenter control keys (quit / pause).
    Returns:
        'quit'     if q key was pressed
        'continue' in all other cases
    """
    keys = event.getKeys(keyList=[task_struct['escape_key'], task_struct['pause_key']])
    if not keys:
        return 'continue'

    # Quit experiment immediately
    if task_struct['escape_key'] in keys:
        task_struct['complete_flag'] = 0
        finish_experiment(task_struct, disp_struct)
        disp_struct['win'].close()
        core.quit()   # hard exit
        return 'quit'  # (won't be reached but nice for clarity)

    # Pause experiment
    if task_struct['pause_key'] in keys:
        event.clearEvents()
        while True:
            keys2 = event.waitKeys(keyList=[task_struct['continue_key'], task_struct['escape_key']])
            if task_struct['escape_key'] in keys2:
                task_struct['complete_flag'] = 0
                finish_experiment(task_struct, disp_struct)
                disp_struct['win'].close()
                core.quit()
            if task_struct['continue_key'] in keys2:
                break
        event.clearEvents()
        return 'continue'

    return 'continue'