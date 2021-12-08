import asyncio
import string


class Timer:
    '''Create an object holding a function to be executed at a later time. Thanks to https://stackoverflow.com/a/45430833

        Arguments:
        
        - timeout -- time (in seconds) to wait before executing callback
        - callback -- function pointer (**NOT** CORO OBJECT) to execute after timeout
        - args -- arguments (if applicable) to be run with callback function'''
    def __init__(self, timeout, callback, *args):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.create_task(self._job(args=args))

    async def _job(self, args):
        await asyncio.sleep(self._timeout)
        await self._callback(*args) if args else await self._callback()

    def cancel(self):
        self._task.cancel()

def convert_time(_time: str) -> tuple:
    '''Convert a given time (i.e. '3d1h') to seconds.'''
    val = str()
    time_obj = dict()
    seconds = int()
    timing_letters = ['d', 'D', 'h', 'H', 'm', 'M', 's', 'S']
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