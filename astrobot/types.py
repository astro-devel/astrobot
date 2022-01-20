from collections import UserString

class FlushingString(UserString):
    """A string object with a method to flush out the content. This can be done with the 'FlushingString.flush()' method."""
    
    def __init__(self, seq=None):
        # probably gonna change this to my own custom implementation at some point because of the idiocracy of
        # UserString not implementing a case if no seq is given, but this works for rn so whatever.
        if not seq:
            super().__init__('')
        else:
            super().__init__(seq)

    def flush(self) -> str:
        """Dump content and reset object data."""
        _tex = self.data
        self.data = ""
        return _tex