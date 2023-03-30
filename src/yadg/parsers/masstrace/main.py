from pydantic import BaseModel
from zoneinfo import ZoneInfo
from . import quadstarsac


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
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
    if filetype == "quadstar.sac":
        return quadstarsac.process(fn, encoding, timezone)
