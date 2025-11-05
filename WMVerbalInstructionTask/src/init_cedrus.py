"""
This function tries a bunch of serial ports onto which the 
button box handle can be created.
"""

import serial
import serial.tools.list_ports

def init_cedrus():
    """
    Initialize CEDRUS response box.
    
    Returns:
    --------
    handle : serial.Serial or None
        Serial port handle for CEDRUS, or None if not found
    """
    # Common COM ports to try
    com_ports = ['COM7', 'COM4', 'COM3', 'COM6', 'COM5', 'COM8', 'COM9']
    
    # Get available COM ports
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    
    for port in com_ports:
        if port in available_ports:
            try:
                handle = serial.Serial(port, baudrate=115200, timeout=0.1)
                # Test if it's actually a CEDRUS box (you might need to adjust this)
                return handle
            except Exception as e:
                print(f"Failed to open {port}: {e}")
                continue
    
    print("Warning: Could not find CEDRUS response box on any COM port")
    return None

