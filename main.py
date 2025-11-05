"""
Main script for verbal instruction task (PsychoPy version).
Run this script to start the task.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

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
    import pickle
    with open(output_file.with_suffix('.pkl'), 'wb') as f:
        pickle.dump({'task_struct': task_struct, 'disp_struct': disp_struct}, f)
    
        # Set up TTL if not in debug mode
    if not task_struct['debug']:
        set_marker_ids()
        # Note: Parallel port setup depends on system configuration
        # For Windows, you may need to use inpout32/inpout64 DLLs
        # This is a placeholder - actual implementation depends on hardware
        try:
            if parallel is None:
                raise ImportError("psychopy.hardware.parallel not available")
            task_struct['parallel_port'] = parallel.ParallelPort(address=0xCFF8)  # Common address
        except (ImportError, Exception) as e:
            print(f"Warning: Could not initialize parallel port. TTL sending disabled. ({e})")
            task_struct['parallel_port'] = None
    
    # Setting up EyeLink if required
    if task_struct['eye_link_mode']:
        file_label = f"VERBAL_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}_sub_{task_struct['sub_id']}"
        fid_log, fname_log, timestamp_str = open_logfile(file_label)
        
        dummy_mode = 0  # Set to 1 to initialize in dummy mode
        edf_filename = f"CS{timestamp_str[-6:]}"
        eyelink_logs_folder = task_code_folder / 'eyelinkLogs'
        eyelink_logs_folder.mkdir(exist_ok=True)
        edf_filename_local = eyelink_logs_folder / f"VERBAL_{timestamp_str}.edf"
        
        # Initialize EyeLink (placeholder - actual implementation needs EyeLink SDK)
        try:
            from psychopy.iohub.client import launchHubServer
            io = launchHubServer()
            tracker = io.devices.tracker
            
            # EyeLink setup would go here
            # ret_code = eye_link_setup(disp_struct['win'], dummy_mode, edf_filename)
            ret_code = 1  # Placeholder
        except ImportError:
            print("Warning: psychopy.iohub not available. EyeLink support disabled.")
            ret_code = 0
        except Exception as e:
            print(f"EyeLink initialization failed: {e}")
            ret_code = 0
        
        if ret_code != 1:
            print('Experiment aborted in eyelink setup screen')
            finish_experiment(task_struct, disp_struct)
            return
        
        task_struct['file_label'] = file_label
        task_struct['fid_log'] = fid_log
        task_struct['fname_log'] = fname_log
        task_struct['timestamp_str'] = timestamp_str
        task_struct['edf_filename'] = edf_filename
        task_struct['edf_filename_local'] = edf_filename_local
        task_struct['ret_code'] = ret_code
    
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

