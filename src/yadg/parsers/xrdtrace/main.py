from . import panalyticalxrdml, panalyticalcsv, panalyticalxy
from dgbowl_schemas.yadg_dataschema.parameters import XRDTrace

version = "4.1.0"


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "UTC",
    parameters: XRDTrace = None,
) -> tuple[list, dict, bool]:
    """
    Unified X-ray diffractogram data parser.

    This parser processes X-ray diffractogram scans in intensity(angle) format.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "UTC".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.parameters.XRDTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. The
        currently implemented parsers all return full date.

    """
    if parameters.filetype == "panalytical.xrdml":
        return panalyticalxrdml.process(fn, encoding, timezone)
    elif parameters.filetype == "panalytical.csv":
        return panalyticalcsv.process(fn, encoding, timezone)
    elif parameters.filetype == "panalytical.xy":
        return panalyticalxy.process(fn, encoding, timezone)
