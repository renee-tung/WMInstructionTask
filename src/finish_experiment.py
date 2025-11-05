"""
This function wraps up after the session, finishing the experiment.
"""

import numpy as np
from intermission_screen import intermission_screen
from send_ttl import send_ttl
from set_marker_ids import *

def finish_experiment(task_struct, disp_struct):
    """
    Finish the experiment and clean up.
    
    Parameters:
    -----------
    task_struct : dict
        Task structure
    disp_struct : dict
        Display structure
    """
    # Final TTL
    if not task_struct['debug']:
        send_ttl(task_struct, 'EXPERIMENT_OFF')
    
    # Wrapping up EyeLink file
    if task_struct['eye_link_mode']:
        print(f'Receiving file and store to: {task_struct.get("edf_filename", "N/A")} '
              f'to {task_struct.get("edf_filename_local", "N/A")}')
        # EyeLink file receive would go here
        # Eyelink('ReceiveFile', task_struct['edf_filename'], task_struct['edf_filename_local'])
        write_log_with_eyelink(task_struct, 'EXPERIMENT_OFF', '')
        # Eyelink('Message', 'Regular Stop')
        # Eyelink('StopRecording')
        # Eyelink('CloseFile')
        # Eyelink('Shutdown')
    
    # End of session message on screen
    if 'correct_responses' in task_struct and 'resp_key' in task_struct:
        correct = np.array(task_struct['correct_responses'])
        resp = np.array(task_struct['resp_key'])
        block_accuracy = 100 * np.nansum(correct == resp) / task_struct['n_trials']
        intermission_screen(
            f'End of session! \n Your final accuracy was {block_accuracy:.1f}%',
            task_struct, disp_struct
        )
    else:
        intermission_screen('End of session!', task_struct, disp_struct)
    
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

