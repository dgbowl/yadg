from pydantic import BaseModel
from . import quadstarsac


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
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
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.MassTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag.

    """
    if parameters.filetype == "quadstar.sac":
        _data, _meta = quadstarsac.process(fn, encoding, timezone)
    return _data, _meta, True
