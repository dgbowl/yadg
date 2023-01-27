from pydantic import BaseModel
from zoneinfo import ZoneInfo
from . import phispe


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
) -> tuple[list, dict, bool]:
    """Unified x-ray photoelectron spectroscopy parser.

    This parser processes XPS scans in signal(energy) format.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "UTC".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.XPSTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag.
        Multipak .spe files seemingly have no timestamp.

    """
    if filetype == "phi.spe":
        return phispe.process(fn, encoding, timezone)
