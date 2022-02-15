import time
import asyncio


class BaseTimer:
    """Create an object holding a function to be executed at a later time. This is to be used as a subclass for astrobot timers. Thanks to https://stackoverflow.com/a/45430833

    Arguments:

    - timeout -- time (in seconds) to wait before executing callback
    - callback -- function pointer (**NOT** CORO OBJECT) to execute after timeout
    - args -- arguments (if applicable) to be run with callback function"""

    def __init__(self, timeout, callback, *args):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.create_task(self._job(args=args))
        self.expires_at = int(time.time()) + timeout

    async def _job(self, args):
        await asyncio.sleep(self._timeout)
        await self._callback(*args) if args else await self._callback()

    def cancel(self):
        self._task.cancel()


class RemindersTimer(BaseTimer):
    """Timer object for reminders."""

    def __init__(self, timeout, callback, *args, reminder_text=None):
        super().__init__(timeout, callback, *[*args, self])
        self.reminder_text = reminder_text


__all__ = ["BaseTimer", "RemindersTimer"]
