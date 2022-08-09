import logging
import json
from pydantic import BaseModel
from . import drycal
from ... import dgutils

logger = logging.getLogger(__name__)


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
    """
    Flow meter data processor

    This parser processes flow meter data.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.FlowData`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. Whether full date
        is returned depends on the file parser.

    """
    if parameters.calfile is not None:
        dgutils.helpers.deprecated("parameters.calfile")
        with open(parameters.calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if parameters.convert is not None:
        dgutils.helpers.deprecated("parameters.convert")
        calib.update(parameters.convert)

    metadata = {}

    if parameters.filetype.startswith("drycal"):
        fulldate = False

        if parameters.filetype.endswith(".rtf") or fn.endswith("rtf"):
            ts, meta = drycal.rtf(fn, encoding, timezone, calib)
        elif parameters.filetype.endswith(".csv") or fn.endswith("csv"):
            ts, meta = drycal.sep(fn, ",", encoding, timezone, calib)
        elif parameters.filetype.endswith(".txt") or fn.endswith("txt"):
            ts, meta = drycal.sep(fn, "\t", encoding, timezone, calib)

        # check timestamps are increasing:
        warn = True
        ndays = 0
        for i in range(1, len(ts)):
            if ts[i]["uts"] < ts[i - 1]["uts"]:
                if warn:
                    logger.warning("DryCal log crossing day boundary. Adding offset.")
                    warn = False
                uts = ts[i]["uts"] + ndays * 86400
                while uts < ts[i - 1]["uts"]:
                    ndays += 1
                    uts = ts[i]["uts"] + ndays * 86400
                ts[i]["uts"] = uts

    metadata.update(meta)

    return ts, metadata, fulldate
