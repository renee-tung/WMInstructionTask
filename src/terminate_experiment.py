"""
Terminate experiment function.
Called when experiment needs to be aborted early (e.g., EyeLink setup failure).
"""

def terminate_experiment(disp_struct, fid_log=None, eye_link_mode=False):
    """
    Terminate experiment early and clean up resources.
    
    Parameters:
    -----------
    disp_struct : dict
        Display structure containing window handle
    fid_log : file object, optional
        Log file handle to close
    eye_link_mode : bool
        Whether EyeLink was being used
    """
    # Close log file if open
    if fid_log is not None:
        try:
            fid_log.close()
        except Exception:
            pass
    
    # Close EyeLink if it was initialized
    if eye_link_mode:
        try:
            from psychopy.iohub import launchHubServer  # type: ignore
            io = launchHubServer()
            if 'tracker' in io.devices:
                tracker = io.devices.tracker
                try:
                    tracker.setRecordingState(False)
                except:
                    pass
        except Exception:
            pass
    
    # Close window if it exists
    if 'win' in disp_struct and disp_struct['win'] is not None:
        try:
            disp_struct['win'].close()
        except Exception:
            pass
    
    print("Experiment terminated early")

