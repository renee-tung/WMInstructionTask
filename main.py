"""
Main script for verbal instruction task (PsychoPy version).
Run this script to start the task.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import pickle

from psychopy import core, visual, event
# Optional hardware imports - only needed if TTL/EyeLink are used
try:
    from psychopy.hardware import parallel
except ImportError:
    parallel = None

# Import local modules
from src.init_task import init_task
from src.run_session import run_session
from src.finish_experiment import finish_experiment
from src.set_marker_ids import set_marker_ids
from src.send_ttl import send_ttl
from src.open_logfile import open_logfile
from src.config_io import config_io
from src.eye_link_setup import eye_link_setup
from src.terminate_experiment import terminate_experiment

# Set up base folder
basefolder = Path(__file__).parent.parent.parent
task_code_folder = basefolder / 'WMVerbalInstructionTask' / 'src'
os.chdir(task_code_folder)

def main():
    """Main function to run the verbal instruction task."""
    
    # Initialize task parameters
    task_struct, disp_struct = init_task()
    
    # Save initial task structure
    output_file = task_struct['output_folder'] / task_struct['file_name']
    with open(output_file.with_suffix('.pkl'), 'wb') as f:
        pickle.dump({'task_struct': task_struct, 'disp_struct': disp_struct}, f)
    
    # Set up TTL if not in debug mode
    if not task_struct['debug']:
        set_marker_ids()
        # Configure parallel port for TTL sending
        task_struct['parallel_port'] = config_io()
    
    # Setting up EyeLink if required
    if task_struct['eye_link_mode']:
        file_label = f"VERBAL_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}_sub_{task_struct['sub_id']}"
        fid_log, fname_log, timestamp_str = open_logfile(file_label)
        
        dummy_mode = 0  # Set to 1 to initialize in dummy mode
        edf_filename = f"CS{timestamp_str[-6:]}"
        eyelink_logs_folder = task_code_folder / 'eyelinkLogs'
        eyelink_logs_folder.mkdir(exist_ok=True)
        edf_filename_local = eyelink_logs_folder / f"VERBAL_{timestamp_str}.edf"
        
        # Initialize EyeLink
        ret_code, tracker = eye_link_setup(disp_struct['win'], dummy_mode, edf_filename)
        
        if ret_code != 1:
            # Aborted - terminate experiment early
            terminate_experiment(disp_struct, fid_log, task_struct['eye_link_mode'])
            print('Experiment aborted in eyelink setup screen')
            return
        
        # EyeLink setup succeeded
        try:
            # Send initial EyeLink messages
            if tracker is not None:
                # Note: Actual EyeLink message sending depends on SDK implementation
                # tracker.sendMessage(fname_log)
                # tracker.sendCommand('record_status_message "NO exp init"')
                pass
        except Exception as e:
            print(f"Warning: Could not send initial EyeLink messages: {e}")
        
        # Write log entry
        from src.finish_experiment import write_log_with_eyelink
        write_log_with_eyelink({'fid_log': fid_log}, 'EXPERIMENT_ON_REAL', '')
        
        task_struct['file_label'] = file_label
        task_struct['fid_log'] = fid_log
        task_struct['fname_log'] = fname_log
        task_struct['timestamp_str'] = timestamp_str
        task_struct['edf_filename'] = edf_filename
        task_struct['edf_filename_local'] = edf_filename_local
        task_struct['ret_code'] = ret_code
        task_struct['tracker'] = tracker  # Store tracker object
    
    # First TTL
    if not task_struct['debug']:
        send_ttl(task_struct, 'EXPERIMENT_ON')
    
    # Run the task
    task_struct, disp_struct = run_session(task_struct, disp_struct)
    
    # Save data to file
    with open(output_file.with_suffix('.pkl'), 'ab') as f:
        pickle.dump({'task_struct': task_struct, 'disp_struct': disp_struct}, f)
    
    # Finishing up
    finish_experiment(task_struct, disp_struct)
    
    # Close the window
    disp_struct['win'].close()
    core.quit()

if __name__ == '__main__':
    main()

