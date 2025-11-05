"""
Sends a TTL value via parallel port.
"""

from set_marker_ids import *

def send_ttl(task_struct, marker_name):
    """
    Send a TTL value via parallel port.
    
    Parameters:
    -----------
    task_struct : dict
        Task structure containing parallel port handle and debug flag
    marker_name : str
        Name of the marker (e.g., 'STIMULUS_ON', 'EXPERIMENT_ON')
    """
    if task_struct['debug']:
        return
    
    if 'parallel_port' not in task_struct or task_struct['parallel_port'] is None:
        return
    
    # Get the marker value from the constants
    try:
        marker_value = globals()[marker_name]
    except KeyError:
        print(f"Warning: Unknown marker name {marker_name}")
        return
    
    # Send TTL via parallel port
    try:
        # For Windows 64-bit with common address 0xCFF8
        # Actual address may vary: 0xCFF8, 0x378, 0x278, etc.
        task_struct['parallel_port'].setData(marker_value)
        # Small delay to ensure signal is sent
        import time
        time.sleep(0.001)
        task_struct['parallel_port'].setData(0)  # Reset to 0
    except Exception as e:
        print(f"Warning: Could not send TTL {marker_name}: {e}")

