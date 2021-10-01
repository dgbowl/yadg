import dgutils

def process(fn: str, **kwargs: dict) -> tuple[list, None, None]:
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
