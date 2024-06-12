"""
This module includes shared functions for the :mod:`~yadg.extractors.drycal`
extractor, including functions for parsing the files, processing the tabulated data,
and ensuring timestamps are increasing.

.. codeauthor::
    Peter Kraus

"""

from pydantic import BaseModel
from typing import Optional
from xarray import Dataset
import logging
import xarray as xr
from striprtf.striprtf import rtf_to_text

from yadg import dgutils
from yadg.extractors.basic.csv import process_row

logger = logging.getLogger(__name__)


class TimeDate(BaseModel):
    class TimestampSpec(BaseModel, extra="forbid"):
        index: Optional[int] = None
        format: Optional[str] = None

    date: Optional[TimestampSpec] = None
    time: Optional[TimestampSpec] = None


def rtf(
    fn: str,
    encoding: str,
    timezone: str,
) -> Dataset:
    with open(fn, "r", encoding=encoding) as infile:
        rtf = infile.read()
    lines = rtf_to_text(rtf).split("\n")
    for li in range(len(lines)):
        if lines[li].startswith("Sample"):
            si = li
        elif lines[li].startswith("1|"):
            di = li
            break
    # Metadata processing for rtf files is in columns, not rows.
    ml = []
    metadata = dict()
    for line in lines[:si]:
        if line.strip() != "":
            items = [i.strip() for i in line.split("|")]
            if len(items) > 1:
                ml.append(items)
    assert len(ml) == 2 and len(ml[0]) == len(ml[1])
    for i in range(len(ml[0])):
        if ml[0][i] != "":
            metadata[ml[0][i]] = ml[1][i]

    # Process data table
    dl = []
    dl.append(" ".join(lines[si:di]))
    for line in lines[di:]:
        if line.strip() != "":
            dl.append(line)
    headers, units, data = drycal_table(dl, sep="|")
    datecolumns, datefunc, _ = dgutils.infer_timestamp_from(
        spec=TimeDate(time={"index": 4, "format": "%I:%M:%S %p"}), timezone=timezone
    )

    # Process rows
    data_vals = {}
    meta_vals = {"_fn": []}
    for pi, point in enumerate(data):
        vals, devs = process_row(headers[1:], point[1:], datefunc, datecolumns)
        dgutils.append_dicts(vals, devs, data_vals, meta_vals, fn, pi)

    return dgutils.dicts_to_dataset(data_vals, meta_vals, units, False)


def sep(
    fn: str,
    sep: str,
    encoding: str,
    timezone: str,
) -> Dataset:
    with open(fn, "r", encoding=encoding) as infile:
        lines = infile.readlines()
    for li in range(len(lines)):
        if lines[li].startswith("Sample"):
            si = li
        elif lines[li].startswith(f"1{sep}"):
            di = li
            break
    # Metadata processing for csv files is standard.
    metadata = dict()
    for line in lines[:si]:
        if line.strip() != "":
            items = [i.strip() for i in line.split(sep)]
            if len(items) == 2:
                metadata[items[0]] = items[1]

    # Process data table
    dl = list()
    dl.append(" ".join(lines[si:di]))
    for line in lines[di:]:
        if line.strip() != "":
            dl.append(line)
    headers, units, data = drycal_table(dl, sep=sep)

    if "AM" in data[0][-1].upper() or "PM" in data[0][-1].upper():
        fmt = "%I:%M:%S %p"
    else:
        fmt = "%H:%M:%S"
    datecolumns, datefunc, _ = dgutils.infer_timestamp_from(
        spec=TimeDate(time={"index": 4, "format": fmt}), timezone=timezone
    )

    # Process rows
    data_vals = {}
    meta_vals = {"_fn": []}
    for pi, point in enumerate(data):
        vals, devs = process_row(headers[1:], point[1:], datefunc, datecolumns)
        dgutils.append_dicts(vals, devs, data_vals, meta_vals, fn, pi)

    return dgutils.dicts_to_dataset(data_vals, meta_vals, units, False)


def drycal_table(lines: list, sep: str = ",") -> tuple[list, dict, list]:
    """
    DryCal table-processing function.

    Given a table with headers and units in the first line, and data in the following
    lines, this function returns the headers, units, and data extracted from the table.
    The returned values are always of :class:`(str)` type, any post-processing is done
    in the calling routine.
    """
    items = [i.strip() for i in lines[0].split(sep)]
    headers = []
    units = {}
    data = []
    trim = False
    for item in items:
        for rs in [". ", " "]:
            parts = item.split(rs)
            if len(parts) == 2:
                break
        headers.append(parts[0])
        if len(parts) == 2:
            units[parts[0]] = parts[1]
        else:
            units[parts[0]] = " "
    if items[-1] == "":
        trim = True
        headers = headers[:-1]
    for line in lines[1:]:
        cols = line.split(sep)
        assert len(cols) == len(items)
        if trim:
            data.append(cols[:-1])
        else:
            data.append(cols)

    units = dgutils.sanitize_units(units)
    return headers, units, data


def check_timestamps(vals: Dataset) -> Dataset:
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
