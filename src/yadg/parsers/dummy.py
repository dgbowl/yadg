import os
from helpers import dateutils

def process(fn, **kwargs):
    """
    A dummy parser.

    This parser checks whether the file specified in `fn` exists.

    Parameters
    ----------
    fn : string
        Filename to check
    
    """
    
    result = {
            "uts": dateutils.now(),
            "fn": fn,
            "exists": os.path.exists(fn)
    }
    
    return [result]
