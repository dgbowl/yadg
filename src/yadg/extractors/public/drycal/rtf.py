import xarray as xr
from zoneinfo import ZoneInfo
from yadg.parsers.flowdata import drycal

supports = {
    "drycal.rtf",
}


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    **kwargs: dict,
) -> xr.Dataset:
    """ """
    vals = drycal.rtf(fn, encoding, timezone)
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


__all__ = ["supports", "extract"]
