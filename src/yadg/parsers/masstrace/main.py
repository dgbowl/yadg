from yadg.parsers.masstrace import quadstarsac


version = "4.0.0"


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    tracetype: str = "quadstar.sac",
) -> tuple[list, dict, None]:
    """Unified mass spectrometry data parser.

    This parser processes mass spectrometry scans in signal(mass) format.

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
        can be found :ref:`here<parsers_masstrace_formats>`.

        The default is ``"quadstar.sac"``.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.

    """
    if tracetype == "quadstar.sac":
        _data, _meta = quadstarsac.process(fn, encoding, timezone)
    return _data, _meta, None
