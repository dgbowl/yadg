from yadg.parsers.electrochem import eclabmpr, eclabmpt

version = "4.1.0"


def process(
    fn: str,
    encoding: str = "windows-1252",
    timezone: str = "localtime",
    filetype: str = "eclab.mpr",
) -> tuple[list, dict, bool]:
    """Unified parser for electrochemistry data.

    Parameters
    ----------
    fn
        The file containing the data to parse.

    encoding
        Encoding of ``fn``, by default "windows-1252".

    timezone
        A string description of the timezone. Default is "localtime".

    filetype
        Determines the output file format. Currently supported formats
        can be found :ref:`here<parsers_electrochem_formats>`.

        The default is ``eclab.mpr`` (auto).

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. The currently
        implemented parsers all return full date.

    """
    if filetype == "eclab.mpr":
        data, meta, fulldate = eclabmpr.process(fn, encoding, timezone)
    elif filetype == "eclab.mpt":
        data, meta, fulldate = eclabmpt.process(fn, encoding, timezone)
    return data, meta, fulldate
