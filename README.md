# Verbal Instruction Task - PsychoPy Conversion

This folder contains the PsychoPy (Python) version of the Verbal Instruction Task, converted from the original Psychtoolbox (MATLAB) code.

## Overview

The Verbal Instruction Task presents participants with visual stimuli and verbal instructions, requiring them to make decisions based on the instructions. The task supports both training and main experimental versions.

## Files

### Main Scripts
- `main.py` - Main script for the experimental task
- `main_training.py` - Main script for the training version

### Core Functions
- `init_task.py` - Initialize task parameters and display for main task
- `init_task_training.py` - Initialize task parameters for training
- `run_session.py` - Run the experimental session (main task)
- `run_session_training.py` - Run the training session
- `finish_experiment.py` - Clean up after main experiment
- `finish_experiment_training.py` - Clean up after training

### Helper Functions
- `get_instruction_text.py` - Generate instruction text based on trial parameters
- `get_correct_responses.py` - Calculate correct responses for trials
- `intermission_screen.py` - Display intermission/break screens
- `send_ttl.py` - Send TTL pulses via parallel port
- `set_marker_ids.py` - Define TTL marker IDs
- `open_logfile.py` - Create log files for data recording
- `init_cedrus.py` - Initialize CEDRUS response box

## Requirements

### Python Packages
- `psychopy` - PsychoPy library for experimental control
- `numpy` - Numerical operations
- `pyserial` - Serial communication (for CEDRUS)
- `pickle` - Data serialization (built-in)

Install with:
```bash
pip install psychopy numpy pyserial
```

### Hardware Support
- **Parallel Port**: For TTL sending (requires appropriate drivers on Windows)
- **EyeLink**: For eye tracking (requires EyeLink SDK)
- **CEDRUS**: For button box responses (optional)

## Usage

### Running the Main Task
```bash
python main.py
```

### Running the Training Version
```bash
python main_training.py
```

## Configuration

### Debug Mode
Set `debug = 1` in the initialization scripts to:
- Skip TTL sending
- Use smaller window size
- Bypass sync tests

### Input Devices
- **Keyboard**: Default input method (Left/Right arrow keys)
- **CEDRUS**: Set `use_cedrus = 1` to use button box

### EyeLink
Set `eye_link_mode = 1` to enable eye tracking. Requires EyeLink SDK integration.

## Differences from MATLAB Version

1. **Data Storage**: Uses pickle files instead of .mat files
2. **Path Handling**: Uses `pathlib.Path` for cross-platform compatibility
3. **Window Management**: Uses PsychoPy's Window class instead of Screen('OpenWindow')
4. **Timing**: Uses `core.getTime()` and `core.wait()` instead of `GetSecs()` and `WaitSecs()`
5. **Stimuli**: Uses `visual.ImageStim` instead of `Screen('MakeTexture')`

## Notes

- TTL sending requires parallel port configuration. The default address (0xCFF8) may need adjustment.
- EyeLink integration requires the EyeLink SDK and proper setup.
- CEDRUS button box support is implemented but may need device-specific adjustments.
- Stimulus paths assume the same folder structure as the MATLAB version.

## Troubleshooting

### Parallel Port Issues
- Check parallel port address in `send_ttl.py`
- Ensure appropriate drivers are installed (inpout32/inpout64 on Windows)
- Try different addresses: 0xCFF8, 0x378, 0x278

### EyeLink Issues
- Ensure EyeLink SDK is properly installed
- Check EyeLink connection before starting experiment
- Verify dummy mode settings if EyeLink is unavailable

### CEDRUS Issues
- Check COM port availability
- Verify baud rate settings (default: 115200)
- May need device-specific command protocols

## Data Output

Data is saved as pickle files in:
- Main task: `../patientData/taskLogs/`
- Training: `../patientData/trainingLogs/`

Each file contains:
- `task_struct`: All task parameters and trial data
- `disp_struct`: Display configuration

## License

This code built off of a task written by Tomas Aquino in PsychToolbox, found here: https://github.com/43technetium/VerbalInstructionTask
Cursor was used to adapt this task

