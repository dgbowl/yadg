from pydantic import BaseModel
from . import phispe


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "UTC",
    parameters: BaseModel = None,
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
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.parameters.dataschema_4_1.XPSTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag.
        Multipak .spe files seemingly have no timestamp.

    """
    if parameters.filetype == "phi.spe":
        return phispe.process(fn, encoding, timezone)
