import logging
from pydantic import BaseModel
from zoneinfo import ZoneInfo

from . import (
    fusionjson,
    fusionzip,
    fusioncsv,
    empalccsv,
    empalcxlsx,
)

logger = logging.getLogger(__name__)


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
) -> tuple[list, dict, bool]:
    """
    Unified chromatographic data parser.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.dataschema_4_2.step.ChromData`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. All currently
        supported file formats return full date.
    """
    if filetype == "fusion.json":
        return fusionjson.process(fn, encoding, timezone)
    elif filetype == "fusion.zip":
        return fusionzip.process(fn, encoding, timezone)
    elif filetype == "fusion.csv":
        return fusioncsv.process(fn, encoding, timezone)
    elif filetype == "empalc.csv":
        return empalccsv.process(fn, encoding, timezone)
    elif filetype == "empalc.xlsx":
        return empalcxlsx.process(fn, encoding, timezone)
