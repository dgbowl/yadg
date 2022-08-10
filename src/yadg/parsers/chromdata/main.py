import logging
from pydantic import BaseModel

from . import (
    fusionjson,
    fusionzip,
    fusioncsv,
    empalccsv,
    empalcxlsx,
)

logger = logging.getLogger(__name__)


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
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
    if parameters.filetype == "fusion.json":
        data, meta, fulldate = fusionjson.process(fn, encoding, timezone)
    elif parameters.filetype == "fusion.zip":
        data, meta, fulldate = fusionzip.process(fn, encoding, timezone)
    elif parameters.filetype == "fusion.csv":
        data, meta, fulldate = fusioncsv.process(fn, encoding, timezone)
    elif parameters.filetype == "empalc.csv":
        data, meta, fulldate = empalccsv.process(fn, encoding, timezone)
    elif parameters.filetype == "empalc.xlsx":
        data, meta, fulldate = empalcxlsx.process(fn, encoding, timezone)

    return data, meta, fulldate
