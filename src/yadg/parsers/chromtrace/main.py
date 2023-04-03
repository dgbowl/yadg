import logging
from zoneinfo import ZoneInfo
from pydantic import BaseModel
import xarray as xr

from . import (
    ezchromasc,
    agilentcsv,
    agilentch,
    agilentdx,
    fusionjson,
    fusionzip,
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
) -> xr.Dataset:
    """
    Unified raw chromatogram parser.

    This parser processes GC and LC chromatograms in signal(time) format. When
    provided with a calibration file, this tool will integrate the trace, and provide
    the peak areas, retention times, and concentrations of the detected species.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.dataschema_4_1.parameters.ChromTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. All currently
        supported file formats return full date.
    """
    if filetype == "ezchrom.asc":
        return ezchromasc.process(fn, encoding, timezone)
    elif filetype == "agilent.csv":
        return agilentcsv.process(fn, encoding, timezone)
    elif filetype == "agilent.dx":
        return agilentdx.process(fn, encoding, timezone)
    elif filetype == "agilent.ch":
        return agilentch.process(fn, encoding, timezone)
    elif filetype == "fusion.json":
        return fusionjson.process(fn, encoding, timezone)
    elif filetype == "fusion.zip":
        return fusionzip.process(fn, encoding, timezone)
