import os
from helpers import dateutils

def process(fn, **kwargs):
    """
    A dummy parser.

    This parser simply returns the current time, the filename provided, and any
    `kwargs` passed.

    Parameters
    ----------
    fn : string
        Filename to check
    
    """
    
    result = {
            "uts": dateutils.now(),
            "fn": fn,
            "kwargs": kwargs
    }
    
    return [result], None, None
