"""
Parallel port configuration function.
Equivalent to MATLAB's config_io.m which sets up io64 interface.
"""

def config_io():
    """
    Configure parallel port for TTL sending.
    This function sets up the parallel port interface for Windows.
    
    Note: On Windows, this typically requires inpout32.dll or inpout64.dll
    For PsychoPy, the parallel port is handled through psychopy.hardware.parallel
    """
    try:
        from psychopy.hardware import parallel
        
        # Try to initialize parallel port
        # Common addresses: 0x378 (LPT1), 0x278 (LPT2), 0xCFF8 (custom)
        # The actual address should match your hardware configuration
        common_addresses = [0x378, 0x278, 0xCFF8]
        
        parallel_port = None
        for address in common_addresses:
            try:
                parallel_port = parallel.ParallelPort(address=address)
                print(f"Parallel port initialized at address 0x{address:X}")
                return parallel_port
            except Exception:
                continue
        
        if parallel_port is None:
            print("Warning: Could not initialize parallel port at any common address")
            print("You may need to specify the correct address for your system")
            return None
            
    except ImportError:
        print("Warning: psychopy.hardware.parallel not available")
        print("Parallel port TTL sending will be disabled")
        return None
    except Exception as e:
        print(f"Parallel port configuration failed: {e}")
        return None

