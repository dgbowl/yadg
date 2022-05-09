from pydantic import BaseModel
from . import eclabmpr, eclabmpt, tomatojson


def process(
    fn: str,
    encoding: str = "windows-1252",
    timezone: str = "localtime",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
    """Unified parser for electrochemistry data.

    Parameters
    ----------
    fn
        The file containing the data to parse.

    encoding
        Encoding of ``fn``, by default "windows-1252".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.parameters.ElectroChem`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. The currently
        implemented parsers all return full date.

    """
    if parameters.filetype == "eclab.mpr":
        data, meta, fulldate = eclabmpr.process(fn, encoding, timezone)
    elif parameters.filetype == "eclab.mpt":
        data, meta, fulldate = eclabmpt.process(fn, encoding, timezone)
    elif parameters.filetype == "tomato.json":
        data, meta, fulldate = tomatojson.process(fn, encoding, timezone)
    return data, meta, fulldate
