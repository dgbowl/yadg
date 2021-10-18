import dgutils

def process(fn: str, encoding: str = "utf-8", 
            **kwargs: dict) -> tuple[list, None, None]:
    """
    A dummy parser.

    This parser simply returns the current time, the filename provided, and any
    `kwargs` passed.

    Parameters
    ----------
    fn
        Filename to process
    encoding
        Encoding of ``fn``, by default "utf-8".
    
    """
    
    result = {
            "uts": dgutils.now(),
            "fn": str(fn),
            "raw": kwargs
    }
    
    return [result], None, None
