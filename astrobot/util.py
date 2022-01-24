from typing import Tuple, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
import string

def time_between(first: datetime, second: datetime) -> str:
    """Get timedelta for two datetimes as a formatted string.
    
        Arguments:
        
        - first (*datetime.datetime) -- the first datetime object
        - second (*datetime.datetime) -- the second datetime object
        
        Return:
        
        - *str -- string representation of timedelta object"""
    _delta = relativedelta(second, first)
    years = _delta.years
    months = _delta.months
    days = _delta.days
    hours = _delta.hours
    mins = _delta.minutes
    secs = _delta.seconds

    return f"""
{years if years else ""}{" Years," if years else ""}
{months if months else ""}{" Months," if months else ""}
{days if days else ""}{" Days," if days else ""}
{hours if hours else ""}{" Hours," if hours else ""}
{mins if mins else ""}{" Minutes," if mins else ""}
{secs if secs else ""}{" Seconds." if secs else ""}""".replace('\n', ' ').strip()

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