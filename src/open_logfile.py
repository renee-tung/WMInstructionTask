"""
Open a text log file for psychophysics experiments.
"""

from datetime import datetime
from pathlib import Path

def open_logfile(label, out_dir=None):
    """
    Open a log file for writing.
    
    Parameters:
    -----------
    label : str
        Label for the log file
    out_dir : str or Path, optional
        Output directory for log files. Defaults to 'c:\\experiments\\logs\\'
    
    Returns:
    --------
    fid : file handle
        File handle for writing
    fname : str
        Full filename (without extension)
    timestamp_str : str
        Timestamp string used in filename
    """
    if out_dir is None:
        out_dir = Path('c:/experiments/logs/')
    else:
        out_dir = Path(out_dir)
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now()
    timestamp_str = f"{now.year}{now.month:02d}{now.day:02d}{now.hour:02d}{now.minute:02d}{int(now.second):02d}"
    
    fname = out_dir / f"{label}{timestamp_str}"
    fid = open(fname.with_suffix('.txt'), 'w+')
    
    return fid, str(fname), timestamp_str

