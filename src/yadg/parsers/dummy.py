import yadg.dgutils

version = "4.0.0"


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "localtime", **kwargs: dict
) -> tuple[list, dict, bool]:
    """
    A dummy parser.

    This parser simply returns the current time, the filename provided, and any
    ``kwargs`` passed.

    Parameters
    ----------
    fn
        Filename to process

    encoding
        Not used.

    timezone
        Not used

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned by the dummy parser. The full date is always returned.

    """

    result = {"uts": yadg.dgutils.now(), "fn": str(fn), "raw": kwargs}

    return [result], None, True
