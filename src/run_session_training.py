"""
This function runs a training verbal instruction task session.
"""

import pdb
import numpy as np
from psychopy import visual, event, core
from psychopy.hardware import keyboard
from pathlib import Path
import pickle


from src.send_ttl import send_ttl
from src.set_marker_ids import *
from src.intermission_screen import intermission_screen
from src.run_session import (get_motor_instruction_text_for_trial, check_for_control_keys, 
                         get_instruction_text_for_trial, write_log_with_eyelink)
from src.photodiode_utils import PhotodiodeFlash

def run_session_training(task_struct, disp_struct):
    """
    Run the training experimental session.
    
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

    if task_struct['blackrock_enabled']:
        from src.send_blackrock_comment import send_blackrock_comment

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
                              units='norm', start=(-0.4, 0.0), end=( 0.4, 0.0),
                              lineWidth=5.0, lineColor=[-1.0, -1.0, -1.0])

    marker = visual.Slider(win=win, name='marker',
                           units='norm', pos=(0.0, 0.0),
                           size=(0.8, 0.08), # 80% of width, 8% of height
                           labels=None, ticks=(-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4),
                           granularity=0.001, style='slider', styleTweaks=('labels45',),
                           opacity=1.0, markerColor=[-1.0, -1.0, -1.0],
                           lineColor=None, labelHeight=0.05, readOnly=False)
    
    # save photodiode obj
    PHOTODIODE = visual.Rect(win, fillColor='white', lineColor='white', 
                             width=disp_struct['photodiode_box'][2], height=disp_struct['photodiode_box'][3], 
                             pos=(disp_struct['photodiode_box'][0], disp_struct['photodiode_box'][1]))
    
    pd_flash = PhotodiodeFlash(
        PHOTODIODE,
        duration=disp_struct['photodiode_dur']
    )

    def send_comment_with_pd(event, task, additional_text):
        """
        Send a Blackrock comment and trigger a short photodiode flash.
        Does nothing in debug mode or if Blackrock is disabled.
        """
        actually_sent_blackrock = False

        if task_struct['blackrock_enabled'] and not task_struct['debug']:
            send_blackrock_comment(
                event=event,
                task=task,
                log_path=task_struct['log_path'],
                additional_text=additional_text
            )
            actually_sent_blackrock = True

        # Photodiode flashes if sent a Blackrock comment, OR in test mode
        if actually_sent_blackrock or task_struct['photodiode_test_mode']:
            pd_flash.trigger()

    def flip_with_pd():
        pd_flash.update()
        return win.flip()

    try:

        for t_i in range(task_struct['n_trials']):
            if t_i == 0:
                intermission_screen('Tutorial: Wait for start!', task_struct, disp_struct)
                intermission_screen('Start when you are ready! \nUse the arrow keys to pick your answer.', task_struct, disp_struct)
            
            if t_i == (task_struct['n_trials'] // 8):
                intermission_screen('Sometimes you will answer with a slider! \nMove the slider further from the center when you are confident. Press space to submit.', task_struct, disp_struct)

            if t_i == (task_struct['n_trials'] // 4):
                intermission_screen('Buttons and sliders will alternate randomly.', task_struct, disp_struct)
            
            if t_i == (task_struct['n_trials'] // 2):
                intermission_screen('Instruction order will now change!', task_struct, disp_struct)
            
            trial_start_time = core.getTime()
            
            # Displaying message on console
            print(f'Trial number {t_i + 1} / {task_struct["n_trials"]}')
            
            # Creating trial struct
            trial_struct = {}
            
            # Presenting fixation cross
            flip_with_pd()
            win.mouseVisible = False
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

            fix_clock = core.Clock()
            first_frame = True

            while fix_clock.getTime() < task_struct['fixation_time'][t_i]:
                fixation_line1.draw()
                fixation_line2.draw()

                if first_frame:
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'FIXATION_ON', '')

                    send_comment_with_pd(
                        event="annotate",
                        task="InstrWM",
                        additional_text=f"trial={t_i}; phase=fixation_on"
                    )

                    trial_struct['fixation1_flip'] = flip_with_pd()
                    first_frame = False
                else:
                    flip_with_pd()
            
            # Check control keys (escape/pause) using helper
            res = check_for_control_keys(task_struct, disp_struct)
            if res == 'quit':
                return task_struct, disp_struct
            
            # Presenting pre-stim instruction (if required)
            if task_struct['trial_cues'][t_i] == 1:
                plotted_text = get_instruction_text_for_trial(task_struct, t_i)

                instruction_text = visual.TextStim(
                    win,
                    text=plotted_text,
                    color='white',
                    height=48,
                    wrapWidth=win.size[0] * 0.8
                )

                instr_clock = core.Clock()
                first_frame = True

                while instr_clock.getTime() < task_struct['instruction_time_max']:
                    instruction_text.draw()

                    if first_frame:
                        # Clear screen just before first instruction frame
                        flip_with_pd()

                        if task_struct['eye_link_mode']:
                            write_log_with_eyelink(task_struct, 'INSTRUCTION_ON', '')

                        send_comment_with_pd(
                            event="annotate",
                            task="InstrWM",
                            additional_text=f"trial={t_i}; phase=instr_task_cue"
                        )

                        trial_struct['instruction1_flip'] = flip_with_pd()
                        first_frame = False
                    else:
                        flip_with_pd()
            
            # Presenting first stimulus
            stim1_position_trial = int(task_struct['stim1_position'][t_i])
            stim1_rect = disp_struct['horizontal_rects'][stim1_position_trial - 1]

            stim1_path = task_struct['trial_stims'][t_i][0]
            stim1_image = visual.ImageStim(
                win,
                image=stim1_path,
                pos=None,
                size=stim1_rect[2] - stim1_rect[0],
                units="pix"
            )
            stim1_image.setPos(((stim1_rect[0] + stim1_rect[2]) / 2,
                                (stim1_rect[1] + stim1_rect[3]) / 2,))

            stim1_clock = core.Clock()
            first_frame = True

            while stim1_clock.getTime() < task_struct['stim1_time']:
                stim1_image.draw()

                if first_frame:
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')

                    send_comment_with_pd(
                        event="annotate",
                        task="InstrWM",
                        additional_text=f"trial={t_i}; phase=stim1_on"
                    )

                    trial_struct['stim1_flip'] = flip_with_pd()
                    first_frame = False
                else:
                    flip_with_pd()

            # Turn off stim1
            trial_struct['stim1_off_flip'] = flip_with_pd()


            # Wait for inter-stimulus interval (with fixation cross)
            isi_clock = core.Clock()
            first_frame = True

            while isi_clock.getTime() < task_struct['ISI'][t_i]:
                fixation_line1.draw()
                fixation_line2.draw()

                if first_frame:
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'DELAY_ON', '')

                    send_comment_with_pd(
                        event="annotate",
                        task="InstrWM",
                        additional_text=f"trial={t_i}; phase=delay_on"
                    )

                    trial_struct['delay_flip'] = flip_with_pd()
                    first_frame = False
                else:
                    flip_with_pd()
            
            # Presenting second stimulus
            stim2_position_trial = int(task_struct['stim2_position'][t_i])
            stim2_rect = disp_struct['horizontal_rects'][stim2_position_trial - 1]
            
            # Load and display image
            stim2_path = task_struct['trial_stims'][t_i][1]
            stim2_image = visual.ImageStim(
                win,
                image=stim2_path,
                pos=None,
                size = stim2_rect[2] - stim2_rect[0],
                units="pix"
            )
            stim2_image.setPos(((stim2_rect[0] + stim2_rect[2])/2, (stim2_rect[1] + stim2_rect[3])/2))

            stim2_clock = core.Clock()
            first_frame = True

            while stim2_clock.getTime() < task_struct['stim2_time']:
                stim2_image.draw()

                if first_frame:
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'STIMULUS_ON', '')

                    send_comment_with_pd(
                        event="annotate",
                        task="InstrWM",
                        additional_text=f"trial={t_i}; phase=stim2_on"
                    )

                    trial_struct['stim2_flip'] = flip_with_pd()
                    first_frame = False
                else:
                    flip_with_pd()

            # Presenting retrocue instruction (if required)
            if task_struct['trial_cues'][t_i] == 2:
                plotted_text = get_instruction_text_for_trial(task_struct, t_i)
                instruction_text = visual.TextStim(
                    win,
                    text=plotted_text,
                    color='white',
                    height=48,
                    wrapWidth=win.size[0] * 0.8
                )

                instr_clock = core.Clock()
                first_frame = True

                while instr_clock.getTime() < task_struct['instruction_time_max']:
                    instruction_text.draw()

                    if first_frame:
                        # Clear screen just before first instruction frame
                        flip_with_pd()

                        if task_struct['eye_link_mode']:
                            write_log_with_eyelink(task_struct, 'INSTRUCTION_ON', '')

                        send_comment_with_pd(
                            event="annotate",
                            task="InstrWM",
                            additional_text=f"trial={t_i}; phase=instr_task_retrocue"
                        )

                        trial_struct['instruction1_flip'] = flip_with_pd()
                        first_frame = False
                    else:
                        flip_with_pd()
                

            # Presenting response instruction (button or slider)
            plotted_text = get_motor_instruction_text_for_trial(task_struct, t_i)
            
            instruction_text = visual.TextStim(
                win,
                text=plotted_text,
                color='white',
                height=48,
                wrapWidth=win.size[0] * 0.8
            )

            resp_instr_clock = core.Clock()
            first_frame = True

            while resp_instr_clock.getTime() < task_struct['response_instruction_time']:
                instruction_text.draw()

                if first_frame:
                    if task_struct['eye_link_mode']:
                        write_log_with_eyelink(task_struct, 'RESP_INSTRUCTION_ON', '')

                    send_comment_with_pd(
                        event="annotate",
                        task="InstrWM",
                        additional_text=f"trial={t_i}; phase=instr_response"
                    )

                    trial_struct['responseinstruction_flip'] = flip_with_pd()
                    first_frame = False
                else:
                    flip_with_pd()


            # Getting response
            if task_struct['response_variants'][t_i] == 1: # slider response
                
                # Display words above the endpoints of the slider
                left_text_stim = visual.TextStim(win, text=task_struct['left_text'][t_i],
                                                color='white', height=48, pos=(-width * 0.4 / 2, height * 0.15))   # left/top

                right_text_stim = visual.TextStim(win, text=task_struct['right_text'][t_i],
                                                color='white', height=48, pos=(width * 0.4 / 2, height * 0.15))    # right/top
                
                reminder_text = visual.TextStim(win, text="Press SPACE to confirm",
                                                color='white', units='norm', 
                                                height=0.05, pos=(0, -0.25))
                
                # left_pressed, right_pressed, marker_moved = 0, 0, 0
                positions = []
                times = []

                slider_min = -0.4
                slider_max = 0.4
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

                marker_moved = 0

                # Set up Cedrus if used
                handle = None
                if task_struct['use_cedrus']:
                    handle = task_struct.get('handle', None)
                    if handle:
                        handle.reset_input_buffer()

                if task_struct['eye_link_mode']:
                    write_log_with_eyelink(task_struct, 'SLIDER_ON', '')
                
                send_comment_with_pd(event="annotate", task="InstrWM", 
                                    additional_text=f"trial={t_i}; phase=slider_on")

                while current_time - cue_time < task_struct['response_time_max']:
                    
                    # Draw existing response frame
                    left_text_stim.draw()
                    right_text_stim.draw()

                    # Draw slider
                    marker.draw()
                    divider_line.draw()
                    slider_line.draw()

                    # Update photodiode status before flipping
                    pd_flash.update()

                    if current_time == cue_time:
                        # trial_struct['response_on_flip'] = win.flip()
                        trial_struct['response_on_flip'] = flip_with_pd()
                    else:
                        # win.flip()
                        flip_with_pd()

                    # Show reminder if enough time passed without confirmation
                    if (current_time - cue_time) > 2:
                        reminder_text.draw()

                    # Check for slider movement
                    keys = slider_resp.getKeys(keyList=['left','right','space'], waitRelease=False, clear=False)
                    key_names = [k.name for k in keys]
                    if 'left' in key_names:
                        # move left
                        marker.markerPos = max(slider_min, marker.markerPos - marker_move)
                    if 'right' in key_names:
                        # move right
                        marker.markerPos = min(slider_max, marker.markerPos + marker_move)
                    
                    if marker.markerPos != 0 and marker_moved == 0:
                        send_comment_with_pd(event="annotate", task="InstrWM", 
                                            additional_text=f"trial={t_i}; phase=slider_moved")
                        marker_moved = 1 # confirm marker moved; don't store TTL again

                    positions.append(marker.markerPos)
                    times.append(current_time - cue_time)
                    
                    if 'space' in key_names: # space to submit

                        # submit
                        rating = marker.markerPos
                        rt = core.getTime() - cue_time
                        
                        # Store response
                        if rating < 0:
                            task_struct['resp_key'][t_i] = 1
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, f"RESPONSE_LEFT", "")
                            send_comment_with_pd(event="annotate", task="InstrWM", 
                                                additional_text=f"trial={t_i}; phase=response_left")
                            left_text_stim.color = 'gray'
                            left_text_stim.draw()
                            right_text_stim.draw()
                            marker.draw()
                            divider_line.draw()
                            slider_line.draw()
                            # trial_struct['response_submit_flip'] = win.flip()
                            trial_struct['response_submit_flip'] = flip_with_pd()
                            core.wait(task_struct['text_holdout_time'])
                            response_received = True
                        elif rating > 0: 
                            task_struct['resp_key'][t_i] = 2
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, f"RESPONSE_RIGHT", "")
                            send_comment_with_pd(event="annotate", task="InstrWM", 
                                                additional_text=f"trial={t_i}; phase=response_right")
                            right_text_stim.color = 'gray'
                            left_text_stim.draw()
                            right_text_stim.draw()
                            marker.draw()
                            divider_line.draw()
                            slider_line.draw()
                            # trial_struct['response_submit_flip'] = win.flip()
                            trial_struct['response_submit_flip'] = flip_with_pd()
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
                    rating = marker.markerPos
                    # rt = core.getTime() - cue_time
                    if rating < 0: 
                        task_struct['resp_key'][t_i] = 1
                    elif rating > 0:
                        task_struct['resp_key'][t_i] = 2
                    task_struct['response_time'][t_i] = np.nan # rt nan since no response
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
                    # lineColor='green',
                    lineColor='black',
                    fillColor=None,
                    lineWidth=5
                )
                bottom_frame = visual.Rect(
                    win,
                    width=bottom_rect[2] - bottom_rect[0],
                    height=bottom_rect[3] - bottom_rect[1],
                    pos=((bottom_rect[0] + bottom_rect[2])/2, (bottom_rect[1] + bottom_rect[3])/2),
                    # lineColor='red',
                    lineColor='black',
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
                
                # trial_struct['response_on_flip'] = win.flip()
                
                if task_struct['eye_link_mode']:
                    write_log_with_eyelink(task_struct, 'BUTTON_ON', '')
                
                send_comment_with_pd(event="annotate", task="InstrWM", 
                                    additional_text=f"trial={t_i}; phase=button_on")
                
                trial_struct['response_on_flip'] = flip_with_pd()
                
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
                                    write_log_with_eyelink(task_struct, 'RESPONSE_UP', '')
                                
                                send_comment_with_pd(event="annotate", task="InstrWM", 
                                                    additional_text=f"trial={t_i}; phase=response_up")
                                # Plotting grayed out selected text
                                top_text_stim.color = 'gray'
                                top_text_stim.draw()
                                top_frame.draw()
                                bottom_frame.draw()
                                bottom_text_stim.draw()
                                pd_flash.update()
                                # trial_struct['response_submit_flip'] = win.flip()
                                trial_struct['response_submit_flip'] = flip_with_pd()

                                core.wait(task_struct['text_holdout_time'])
                                response_received = True
                                break
                            elif key == task_struct['down_key']:
                                task_struct['resp_key'][t_i] = 2
                                if task_struct['eye_link_mode']:
                                    write_log_with_eyelink(task_struct, 'RESPONSE_DOWN', '')
                                send_comment_with_pd(event="annotate", task="InstrWM", 
                                                    additional_text=f"trial={t_i}; phase=response_down")
                                # Plotting grayed out selected text
                                bottom_text_stim.color = 'gray'
                                top_frame.draw()
                                bottom_frame.draw()
                                top_text_stim.draw()
                                bottom_text_stim.draw()
                                # trial_struct['response_submit_flip'] = win.flip()
                                trial_struct['response_submit_flip'] = flip_with_pd()
                                core.wait(task_struct['text_holdout_time'])
                                response_received = True
                                break
                        
                        current_time = core.getTime()
                else:
                    # Keyboard response (using arrow keys)
                    event.clearEvents()
                    response_received = False

                    # Clock for response window
                    resp_clock = core.Clock()
                    first_frame = True

                    while resp_clock.getTime() < task_struct['response_time_max'] and not response_received:
                        # Draw button options every frame
                        top_frame.draw()
                        bottom_frame.draw()
                        top_text_stim.draw()
                        bottom_text_stim.draw()

                        if first_frame:
                            # First frame: log button onset + PD flash
                            if task_struct['eye_link_mode']:
                                write_log_with_eyelink(task_struct, 'BUTTON_ON', '')

                            send_comment_with_pd(
                                event="annotate",
                                task="InstrWM",
                                additional_text=f"trial={t_i}; phase=button_on"
                            )

                            trial_struct['response_on_flip'] = flip_with_pd()
                            # Start response timing from this onset
                            cue_time = trial_struct['response_on_flip']
                            first_frame = False
                        else:
                            flip_with_pd()

                        # Check for key press
                        keys = event.getKeys(
                            keyList=[task_struct['up_key'], task_struct['down_key']],
                            timeStamped=True
                        )

                        if keys:
                            key, time = keys[0]
                            task_struct['response_time'][t_i] = time - cue_time

                            # ---------- RESPONSE: UP (top option) ----------
                            if key == task_struct['up_key']: # response: up
                                task_struct['resp_key'][t_i] = 1
                                if task_struct['eye_link_mode']:
                                    write_log_with_eyelink(task_struct, 'RESPONSE_UP', '')

                                send_comment_with_pd(
                                    event="annotate",
                                    task="InstrWM",
                                    additional_text=f"trial={t_i}; phase=response_up"
                                )

                                # Hold gray-out feedback with its own loop so PD can pulse
                                hold_clock = core.Clock()
                                first_hold_frame = True
                                while hold_clock.getTime() < task_struct['text_holdout_time']:
                                    top_text_stim.color = 'gray'
                                    top_text_stim.draw()
                                    top_frame.draw()
                                    bottom_frame.draw()
                                    bottom_text_stim.draw()

                                    if first_hold_frame:
                                        trial_struct['response_submit_flip'] = flip_with_pd()
                                        first_hold_frame = False
                                    else:
                                        flip_with_pd()

                                response_received = True
                                break

                            # ---------- RESPONSE: DOWN (bottom option) ----------
                            elif key == task_struct['down_key']:
                                task_struct['resp_key'][t_i] = 2
                                if task_struct['eye_link_mode']:
                                    write_log_with_eyelink(task_struct, 'RESPONSE_DOWN', '')

                                send_comment_with_pd(
                                    event="annotate",
                                    task="InstrWM",
                                    additional_text=f"trial={t_i}; phase=response_down"
                                )

                                # Hold gray-out feedback with its own loop so PD can pulse
                                hold_clock = core.Clock()
                                first_hold_frame = True
                                while hold_clock.getTime() < task_struct['text_holdout_time']:
                                    bottom_text_stim.color = 'gray'
                                    top_frame.draw()
                                    bottom_frame.draw()
                                    top_text_stim.draw()
                                    bottom_text_stim.draw()

                                    if first_hold_frame:
                                        trial_struct['response_submit_flip'] = flip_with_pd()
                                        first_hold_frame = False
                                    else:
                                        flip_with_pd()

                                response_received = True
                                break

            
            if task_struct['eye_link_mode']:
                write_log_with_eyelink(task_struct, 'TRIAL_END', '')
            
            send_comment_with_pd(event="annotate", task="InstrWM", 
                                additional_text=f"trial={t_i}; phase=trial_end")
            
            PHOTODIODE.autoDraw = False
            # trial_struct['response_end_flip'] = win.flip()
            trial_struct['response_end_flip'] = flip_with_pd()
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
    except Exception as e:
        print("\n\n*** EXPERIMENT CRASHED ***\n")
        print(type(e), e)

        # send crash message to photodiode/blackrock
        send_comment_with_pd(event="error", task="InstrWM", 
                            additional_text=f"trial={t_i}; error={str(e)}")

        return task_struct, disp_struct

