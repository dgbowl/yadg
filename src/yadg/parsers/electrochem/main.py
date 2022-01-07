from yadg.parsers.electrochem import eclabmpr, eclabmpt

version = "4.0.0"


def process(
    fn: str,
    encoding: str = "windows-1252",
    timezone: str = "localtime",
    filetype: str = "eclab.mpr",
) -> tuple[list, dict, None]:
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
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.

    """
    if filetype == "eclab.mpr":
        data, meta = eclabmpr.process(fn, encoding, timezone)
    elif filetype == "eclab.mpt":
        data, meta = eclabmpt.process(fn, encoding, timezone)
    return data, meta, None
