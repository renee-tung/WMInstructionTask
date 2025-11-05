"""
This function creates a multi-purpose intermission screen to buffer
different stages of the task.
"""

from psychopy import event, visual

def intermission_screen(text, task_struct, disp_struct):
    """
    Display an intermission screen and wait for continue key.
    
    Parameters:
    -----------
    text : str
        Text to display on the intermission screen
    task_struct : dict
        Task structure containing continue key information
    disp_struct : dict
        Display structure containing window handle
    """
    # Displaying same message on console
    print(text)
    
    # Clear screen
    win = disp_struct['win']
    win.flip()
    
    # Create text stimulus
    intermission_text = visual.TextStim(
        win,
        text=text.replace('\\n', '\n'),
        color='white',
        height=48,
        wrapWidth=win.size[0] * 0.8
    )
    
    # Draw and flip
    intermission_text.draw()
    win.flip()
    
    # Wait for continue key to be pressed
    event.clearEvents()
    intermission_over = False
    while not intermission_over:
        keys = event.getKeys(keyList=[task_struct['continue_key']])
        if keys:
            intermission_over = True

