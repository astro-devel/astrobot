from typing import Tuple, Optional
import string

def convert_time(_time: str) -> Tuple[Optional[int], Optional[dict]]:
    """Convert a given time (i.e. '3d1h') to seconds."""
    val = str()
    time_obj = dict()
    seconds = int()
    #timing_letters = ['d', 'D', 'h', 'H', 'm', 'M', 's', 'S']
    for char in _time:
        if char in string.ascii_letters:
            time_obj[char] = val
            val = str()
        else:
            val += char
    
    if not time_obj:
        return (None, None)
    
    try:
        for multiplier, value in time_obj.items():
            if multiplier.lower() == 'd': # 86400 <- 1
                seconds += int(value) * 24 * 60 * 60
            elif multiplier.lower() == 'h': # 3600 <- 1
                seconds += int(value) * 60 * 60
            elif multiplier.lower() == 'm': # 60 <- 1
                seconds += int(value) * 60
            elif multiplier.lower() == 's': # 1 <- 1
                seconds += int(value)
    except ValueError:
        return (None, None)

    return (seconds, time_obj)