from . import quadstarsac
from dgbowl_schemas.yadg_dataschema.parameters import MassTrace

version = "4.0.0"


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: MassTrace = None,
) -> tuple[list, dict, bool]:
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

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.parameters.MassTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag.

    """
    if parameters.filetype == "quadstar.sac":
        _data, _meta = quadstarsac.process(fn, encoding, timezone)
    return _data, _meta, True
