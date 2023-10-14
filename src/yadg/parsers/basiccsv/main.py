import logging
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from typing import Callable, Any
from pydantic import BaseModel
import locale as lc
from ... import dgutils

import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


def process_row(
    headers: list,
    items: list,
    datefunc: Callable,
    datecolumns: list,
) -> tuple[dict, dict]:
    """
    A function that processes a row of a table.

    This is the main worker function of :mod:`~yadg.parsers.basiccsv`, but is often
    re-used by any other parser that needs to process tabular data.

    Parameters
    ----------
    headers
        A list of headers of the table.

    items
        A list of values corresponding to the headers. Must be the same length as headers.

    units
        A dict for looking up the units corresponding to a certain header.

    datefunc
        A function that will generate ``uts`` given a list of values.

    datecolumns
        Column indices that need to be passed to ``datefunc`` to generate uts.

    Returns
    -------
    vals, devs
        A tuple of result dictionaries, with the first element containing the values
        and the second element containing the deviations of the values.

    """
    assert len(headers) == len(items), (
        f"process_row: Length mismatch between provided headers: "
        f"{headers} and  provided items: {items}."
    )

    vals = {}
    devs = {}
    columns = [column.strip() for column in items]

    # Process raw data, assign sigma and units
    vals["uts"] = datefunc(*[columns[i] for i in datecolumns])
    for ci, header in enumerate(headers):
        if ci in datecolumns:
            continue
        elif columns[ci] == "":
            continue
        try:
            val, dev = tuple_fromstr(lc.delocalize(columns[ci]))
            vals[header] = val
            devs[header] = dev
        except ValueError:
            vals[header] = columns[ci]

    return vals, devs


def append_dicts(
    vals: dict[str, Any],
    devs: dict[str, Any],
    data: dict[str, list[Any]],
    meta: dict[str, list[Any]],
    fn: str = None,
    li: int = 0,
) -> None:
    if "_fn" in meta and fn is not None:
        meta["_fn"].append(str(fn))
    for k, v in vals.items():
        if k not in data:
            data[k] = [None if isinstance(v, str) else np.nan] * li
        data[k].append(v)
    for k, v in devs.items():
        if k not in meta:
            meta[k] = [np.nan] * li
        meta[k].append(v)

    for k in set(data) - set(vals):
        data[k].append(np.nan)
    for k in set(meta) - set(devs):
        if k != "_fn":
            meta[k].append(np.nan)


def dicts_to_dataset(
    data: dict[str, list[Any]],
    meta: dict[str, list[Any]],
    units: dict[str, str] = dict(),
    fulldate: bool = True,
) -> xr.Dataset:
    darrs = {}
    for k, v in data.items():
        attrs = {}
        u = units.get(k, None)
        if u is not None:
            attrs["units"] = u
        if k == "uts":
            continue
        darrs[k] = xr.DataArray(data=v, dims=["uts"], attrs=attrs)
        if k in meta and darrs[k].dtype.kind in {"i", "u", "f", "c", "m", "M"}:
            err = f"{k}_std_err"
            darrs[k].attrs["ancillary_variables"] = err
            attrs["standard_name"] = f"{k} standard error"
            darrs[err] = xr.DataArray(data=meta[k], dims=["uts"], attrs=attrs)
    if "uts" in data:
        coords = dict(uts=data.pop("uts"))
    else:
        coords = dict()
    if fulldate:
        attrs = dict()
    else:
        attrs = dict(fulldate=False)
    return xr.Dataset(data_vars=darrs, coords=coords, attrs=attrs)


def process(
    *,
    fn: str,
    encoding: str,
    locale: str,
    timezone: str,
    parameters: BaseModel,
    **kwargs: dict,
) -> xr.Dataset:
    """
    A basic csv parser.

    This parser processes a csv file. The header of the csv file consists of one or two
    lines, with the column headers in the first line and the units in the second. The
    parser also attempts to parse column names to produce a timestamp, and save all other
    columns as floats or strings.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_5_0.step.BasicCSV`.

    Returns
    -------
    :class:`xarray.Dataset`
        No metadata is returned by the :mod:`~yadg.parsers.basiccsv` parser. The full
        date might not be returned, eg. when only time is specified in columns.

    """

    if hasattr(parameters, "strip"):
        strip = parameters.strip
    else:
        strip = None

    # Load file, extract headers and get timestamping function
    with open(fn, "r", encoding=encoding) as infile:
        # This decode/encode is done to account for some csv files that have a BOM
        # at the beginning of each line.
        lines = [i.encode().decode(encoding) for i in infile.readlines()]
    assert len(lines) >= 2
    headers = [h.strip().strip(strip) for h in lines[0].split(parameters.sep)]

    for hi, header in enumerate(headers):
        if "/" in header:
            logger.warning("Replacing '/' for '_' in header '%s'.", header)
            headers[hi] = header.replace("/", "_")

    datecolumns, datefunc, fulldate = dgutils.infer_timestamp_from(
        headers=headers, spec=parameters.timestamp, timezone=timezone
    )

    # Populate units
    units = parameters.units
    if units is None:
        units = {}
        _units = [c.strip().strip(strip) for c in lines[1].split(parameters.sep)]
        for header in headers:
            units[header] = _units.pop(0)
        si = 2
    else:
        for header in headers:
            if header not in units:
                logger.warning(
                    "Using implicit dimensionless unit ' ' for '%s'.", header
                )
                units[header] = " "
            elif units[header] == "":
                units[header] = " "
        si = 1

    units = dgutils.sanitize_units(units)

    # Process rows
    old_loc = lc.getlocale(category=lc.LC_NUMERIC)
    lc.setlocale(lc.LC_NUMERIC, locale=locale)
    data_vals = {}
    meta_vals = {"_fn": []}
    for li, line in enumerate(lines[si:]):
        vals, devs = process_row(
            headers,
            [i.strip().strip(strip) for i in line.split(parameters.sep)],
            datefunc,
            datecolumns,
        )
        append_dicts(vals, devs, data_vals, meta_vals, fn, li)
    lc.setlocale(category=lc.LC_NUMERIC, locale=old_loc)

    return dicts_to_dataset(data_vals, meta_vals, units, fulldate)
