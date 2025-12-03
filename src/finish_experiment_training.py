"""
This function wraps up after the training session, finishing the experiment.
"""

from src.intermission_screen import intermission_screen
import numpy as np

def finish_experiment_training(task_struct, disp_struct):
    """
    Finish the training experiment and clean up.
    
    Parameters:
    -----------
    task_struct : dict
        Task structure
    disp_struct : dict
        Display structure
    """
    # Send final Blackrock comment if enabled
    if task_struct['blackrock_enabled']:
        from src.send_blackrock_comment import send_blackrock_comment
        send_blackrock_comment(event="stop", task="DCWM", 
                               log_path=task_struct['log_path'])
    
    # Wrapping up EyeLink file
    if task_struct['eye_link_mode']:
        print(f'Receiving file and store to: {task_struct.get("edf_filename", "N/A")} '
              f'to {task_struct.get("edf_filename_local", "N/A")}')
        write_log_with_eyelink(task_struct, 'EXPERIMENT_OFF', '')
    
    # End of tutorial message on screen
    if 'correct_responses' in task_struct and 'resp_key' in task_struct:
        correct = np.array(task_struct['correct_responses'])
        resp = np.array(task_struct['resp_key'])
        block_accuracy = 100 * np.nansum(correct == resp) / task_struct['n_trials']
        intermission_screen(
            f'End of tutorial! \n Your final accuracy was {block_accuracy:.1f}%',
            task_struct, disp_struct
        )
    else:
        intermission_screen('End of tutorial!', task_struct, disp_struct)
    
    # Close log file if open
    if 'fid_log' in task_struct and task_struct['fid_log']:
        task_struct['fid_log'].close()


def write_log_with_eyelink(task_struct, event_name, message):
    """Write log entry with EyeLink."""
    if 'fid_log' in task_struct and task_struct['fid_log']:
        import time
        timestamp = time.time()
        log_entry = f"{timestamp}\t{event_name}\t{message}\n"
        task_struct['fid_log'].write(log_entry)
        task_struct['fid_log'].flush()

