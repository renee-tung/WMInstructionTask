"""
EyeLink setup and calibration function.
Adapted from EyelinkImageExample.m demo file.
"""

def eye_link_setup(window, dummy_mode, edf_filename):
    """
    Initialize and calibrate EyeLink tracker.
    
    Parameters:
    -----------
    window : psychopy.visual.Window
        PsychoPy window object
    dummy_mode : int
        0 = real mode, 1 = dummy mode
    edf_filename : str
        EDF filename for recording
    
    Returns:
    --------
    ret_code_success : int
        1 if succeeded, 0 if failed
    tracker : object
        EyeLink tracker object (if available)
    """
    ret_code_success = 1  # 1 if succeeded, 0 if failure
    
    try:
        from psychopy.iohub import launchHubServer  # type: ignore
        from psychopy.iohub.devices.eyetracker import EyeTrackerDevice  # type: ignore
        
        # Initialize ioHub
        io = launchHubServer()
        
        # Get EyeLink tracker
        tracker = None
        if 'eyetracker' in io.devices:
            tracker = io.devices.eyetracker
        elif 'tracker' in io.devices:
            tracker = io.devices.tracker
        
        if tracker is None:
            print("Warning: EyeLink tracker not found in ioHub devices")
            ret_code_success = 0
            return ret_code_success, None
        
        # Initialize EyeLink
        if not dummy_mode:
            try:
                tracker.runSetupProcedure()
            except Exception as e:
                print(f"EyeLink Init aborted: {e}")
                ret_code_success = 0
                return ret_code_success, None
        
        # Get tracker version
        try:
            tracker_version = tracker.getTrackerVersion()
            print(f"Running experiment on a '{tracker_version}' tracker.")
        except:
            print("Could not get tracker version")
        
        # Open file for recording
        edf_file = f"{edf_filename}.edf"
        try:
            tracker.setRecordingState(False)  # Stop any existing recording
            tracker.setConnectionState(True)  # Ensure connected
            # Note: Actual EDF file opening depends on EyeLink SDK implementation
            print(f"EDF filename: {edf_file}")
        except Exception as e:
            print(f"Warning: Could not open EDF file: {e}")
        
        # Do setup and calibrate the eye tracker
        if not dummy_mode:
            print("Running EyeLink setup...")
            try:
                # Run calibration/setup procedure
                setup_result = tracker.runSetupProcedure()
                
                if setup_result == 0:
                    # Do a final check of calibration using drift correction
                    print("Running EyeLink drift correction...")
                    drift_result = tracker.runDriftCorrect()
                    
                    if drift_result == 0:
                        # Start recording eye position
                        tracker.setRecordingState(True)
                        # Record a few samples before we actually start displaying
                        import time
                        time.sleep(0.5)
                        
                        ret_code_success = 1
                    else:
                        print("Drift correction failed")
                        ret_code_success = 0
                else:
                    print("EyeLink setup failed")
                    ret_code_success = 0
            except Exception as e:
                print(f"EyeLink setup error: {e}")
                ret_code_success = 0
        else:
            # Dummy mode - just mark as successful
            ret_code_success = 1
        
        return ret_code_success, tracker
        
    except ImportError:
        print("Warning: psychopy.iohub not available. EyeLink support disabled.")
        ret_code_success = 0
        return ret_code_success, None
    except Exception as e:
        print(f"EyeLink initialization failed: {e}")
        ret_code_success = 0
        return ret_code_success, None

