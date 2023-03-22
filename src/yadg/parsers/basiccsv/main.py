import logging
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from typing import Callable
from pydantic import BaseModel
from ... import dgutils

import numpy as np
from datatree import DataTree
from xarray import DataArray, Dataset

logger = logging.getLogger(__name__)


def process_row(
    headers: list,
    items: list,
    datefunc: Callable,
    datecolumns: list,
) -> dict:
    """
    A function that processes a row of a table.

    This is the main worker function of ``basiccsv``, but can be re-used by any other
    parser that needs to process tabular data.

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
    element: dict
        A result dictionary, containing the keys ``"uts"`` with a timestamp,
        ``"raw"`` for all raw data present in the headers, and ``"derived"``
        for any data processes via ``calib``.

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
            val, dev = tuple_fromstr(columns[ci])
            vals[header] = val
            devs[header] = dev
        except ValueError:
            vals[header] = columns[ci]

    return vals, devs


def process(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    locale: str,
    filetype: str,
    parameters: BaseModel,
) -> tuple[list, dict, bool]:
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
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.BasicCSV`.

    Returns
    -------
    dt: datatree.DataTree
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned by the basiccsv parser. The full date might not be returned, eg.
        when only time is specified in columns.

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
    data_vals = {}
    meta_vals = {"_fn": []}
    for li, line in enumerate(lines[si:]):
        vals, devs = process_row(
            headers,
            [i.strip().strip(strip) for i in line.split(parameters.sep)],
            datefunc,
            datecolumns,
        )
        meta_vals["_fn"].append(str(fn))
        for k, v in vals.items():
            if k not in data_vals:
                data_vals[k] = [None if isinstance(v, str) else np.nan] * li
            data_vals[k].append(v)
        for k, v in devs.items():
            if k not in meta_vals:
                meta_vals[k] = [np.nan] * li
            meta_vals[k].append(v)

        for k in set(data_vals) - set(vals):
            data_vals[k].append(np.nan)
        for k in set(meta_vals) - set(devs):
            if k != "_fn":
                meta_vals[k].append(np.nan)

    for k, v in data_vals.items():
        attrs = {}
        u = units.get(k, None)
        if u is not None:
            attrs["units"] = u
        if k == "uts":
            attrs["fulldate"] = fulldate
        data_vals[k] = DataArray(data=v, dims=["uts"], attrs=attrs)

    for k, v in meta_vals.items():
        meta_vals[k] = DataArray(data=v, dims=["uts"])

    coords = {"uts": data_vals.pop("uts")}
    dt = DataTree.from_dict(
        {
            "/": Dataset(data_vars=data_vals, coords=coords),
            "/_yadg.meta": Dataset(data_vars=meta_vals, coords=coords),
        }
    )
    print(f"{dt=}")
    return dt
