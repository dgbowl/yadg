import logging
import xarray as xr
from zoneinfo import ZoneInfo
from . import drycal

logger = logging.getLogger(__name__)


def process(
    *,
    fn: str,
    filetype: str,
    encoding: str,
    timezone: ZoneInfo,
    **kwargs: dict,
) -> xr.Dataset:
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
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_5_0.step.FlowData`.

    Returns
    -------
    :class:`xarray.Dataset`

    """

    if filetype.startswith("drycal"):

        if filetype.endswith(".rtf") or fn.endswith("rtf"):
            vals = drycal.rtf(fn, encoding, timezone)
        elif filetype.endswith(".csv") or fn.endswith("csv"):
            vals = drycal.sep(fn, ",", encoding, timezone)
        elif filetype.endswith(".txt") or fn.endswith("txt"):
            vals = drycal.sep(fn, "\t", encoding, timezone)

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
        vals["uts"] = xr.DataArray(data=utslist, dims=["uts"])
        vals.attrs["fulldate"] = False
    return vals
