from yadg.parsers.xrdtrace import panalyticalxrdml, panalyticalcsv, panalyticalxy


version = "4.0.0"


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "UTC",
    tracetype: str = "panalytical.xrdml",
) -> tuple[list, dict, bool]:
    """Unified X-ray diffractogram data parser..

    This parser processes X-ray diffractogram scans in intensity(angle).
    format.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "UTC".

    tracetype
        Determines the output file format. Currently supported formats
        can be found :ref:`here<parsers_xrdtrace_formats>`.

        The default is ``"panalytical.xrdml"``.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. The
        currently implemented parsers all return full date.

    """
    if tracetype == "panalytical.xrdml":
        return panalyticalxrdml.process(fn, encoding, timezone)
    if tracetype == "panalytical.csv":
        return panalyticalcsv.process(fn, encoding, timezone)
    if tracetype == "panalytical.xy":
        return panalyticalxy.process(fn, encoding, timezone)
