from yadg.parsers.xpstrace import phispe


version = "4.0.0"


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    tracetype: str = "phi.spe",
) -> tuple[list, dict, None]:
    """Unified x-ray photoelectron spectroscopy parser.

    This parser processes XPS scans in signal(energy) format.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    tracetype
        Determines the output file format. Currently supported formats
        can be found :ref:`here<parsers_xpstrace_formats>`.

        The default is ``"phi.spe"``.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.

    """
    if tracetype == "phi.spe":
        _data, _meta = phispe.process(fn, encoding, timezone)
    return _data, _meta, None
