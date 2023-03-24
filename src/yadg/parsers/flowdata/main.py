import logging
from pydantic import BaseModel
from zoneinfo import ZoneInfo
from . import drycal
from xarray import DataArray
from datatree import DataTree

logger = logging.getLogger(__name__)


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
) -> DataTree:
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

    if filetype.startswith("drycal"):

        if filetype.endswith(".rtf") or fn.endswith("rtf"):
            vals, devs = drycal.rtf(fn, encoding, timezone)
        elif filetype.endswith(".csv") or fn.endswith("csv"):
            vals, devs = drycal.sep(fn, ",", encoding, timezone)
        elif filetype.endswith(".txt") or fn.endswith("txt"):
            vals, devs = drycal.sep(fn, "\t", encoding, timezone)

        # check timestamps are increasing:
        warn = True
        ndays = 0
        utslist = vals.uts.values
        for i in range(1, vals.uts.size):
            if utslist[i] < utslist[i - 1]:
                if warn:
                    logger.warning("DryCal log crossing day boundary. Adding offset.")
                    warn = False
                uts = utslist[i] + ndays * 86400
                while uts < utslist[i - 1]:
                    ndays += 1
                    uts = utslist[i] + ndays * 86400
                utslist[i] = uts
        vals["uts"] = DataArray(data=utslist, dims=["uts"])
        vals.attrs["fulldate"] = False
        devs["_uts"] = DataArray(data=utslist, dims=["_uts"])
    return vals, devs
