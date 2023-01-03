import json
import logging
from pydantic import BaseModel
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
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
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
    if parameters.filetype == "ezchrom.asc":
        _data, _meta = ezchromasc.process(fn, encoding, timezone)
    elif parameters.filetype == "agilent.csv":
        _data, _meta = agilentcsv.process(fn, encoding, timezone)
    elif parameters.filetype == "agilent.dx":
        _data, _meta = agilentdx.process(fn, encoding, timezone)
    elif parameters.filetype == "agilent.ch":
        _data, _meta = agilentch.process(fn, encoding, timezone)
    elif parameters.filetype == "fusion.json":
        _data, _meta = fusionjson.process(fn, encoding, timezone)
    elif parameters.filetype == "fusion.zip":
        _data, _meta = fusionzip.process(fn, encoding, timezone)

    results = []
    for chrom in _data:
        result = {}
        result["uts"] = chrom.pop("uts")
        result["fn"] = chrom.pop("fn")
        result["raw"] = {}
        result["raw"].update(chrom.pop("raw", {}))
        result["raw"].update(chrom)
        results.append(result)

    return results, _meta, True
