"""
Lookup table to determine motor instruction prompt used in each trial (buttons or slider).
"""

def get_motor_instruction_text(response_variant):
    """
    Get motor instruction text based on trial parameters.
    
    Parameters:
    -----------
    response_variant : bool or int
        Which response variant to use (0 for button, 1 for slider)
    
    Returns:
    --------
    text : str
        Instruction text for the trial
    """
    # Convert to boolean for easier handling
    response_variant = bool(response_variant)
    
    # Create text
    if response_variant:
        text = 'Move the slider to answer'
    else:
        text = 'Press the button to answer'
    
    return text

