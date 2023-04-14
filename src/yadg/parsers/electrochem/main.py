from pydantic import BaseModel
from zoneinfo import ZoneInfo
from . import eclabmpr, eclabmpt, tomatojson


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
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
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.ElectroChem`.

    Returns
    -------
    ds: xr.Dataset


    """
    if filetype == "eclab.mpr":
        return eclabmpr.process(fn, timezone)
    elif filetype == "eclab.mpt":
        return eclabmpt.process(fn, encoding, locale, timezone)
    elif filetype == "tomato.json":
        return tomatojson.process(fn)
