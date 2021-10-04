import os
import dgutils

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
            "uts": dgutils.now(),
            "fn": str(fn),
            "kwargs": kwargs
    }
    
    return [result], None, None
