"""
This module includes shared functions for the :mod:`~yadg.extractors.drycal`
extractor, including functions for parsing the files, processing the tabulated data,
and ensuring timestamps are increasing.

.. codeauthor::
    Peter Kraus

"""

import logging
from pydantic import BaseModel
from striprtf.striprtf import rtf_to_text
from typing import Optional
from xarray import Dataset, DataArray
from yadg import dgutils
from yadg.dgutils.table import process_table

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
    headers, units = drycal_header(dl[0], sep="|")
    datecolumns, datefunc, _ = dgutils.infer_timestamp_from(
        spec=TimeDate(time={"index": 5, "format": "%I:%M:%S %p"}), timezone=timezone
    )

    data_vars = process_table(
        lines=dl[1:],
        headers=headers,
        datecolumns=datecolumns,
        datefunc=datefunc,
        sep="|",
    )
    coords = dict(uts=data_vars.pop("uts"))
    attrs = dict(fulldate=False)
    data_vars.pop("Sample")
    data_vars.pop("Sample_uncertainty")

    for k in units:
        if k in data_vars:
            data_vars[k][2]["units"] = units[k]

    ds = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
    return ds


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
    headers, units = drycal_header(dl[0], sep=sep)
    print(dl[1])

    if "AM" in dl[1].upper() or "PM" in dl[1].upper():
        fmt = "%I:%M:%S %p"
    else:
        fmt = "%H:%M:%S"
    datecolumns, datefunc, _ = dgutils.infer_timestamp_from(
        spec=TimeDate(time={"index": 5, "format": fmt}), timezone=timezone
    )

    data_vars = process_table(
        lines=dl[1:],
        headers=headers,
        datecolumns=datecolumns,
        datefunc=datefunc,
        sep=sep,
    )
    coords = dict(uts=data_vars.pop("uts"))
    attrs = dict(fulldate=False)
    data_vars.pop("Sample")
    data_vars.pop("Sample_uncertainty")

    for k in units:
        if k in data_vars:
            data_vars[k][2]["units"] = units[k]

    ds = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
    return ds


def drycal_header(line: str, sep: str = ",") -> tuple[list, dict]:
    """
    DryCal table-processing function.

    Given a table with headers and units in the first line, and data in the following
    lines, this function returns the headers, units, and data extracted from the table.
    The returned values are always of :class:`(str)` type, any post-processing is done
    in the calling routine.
    """
    items = [i.strip() for i in line.split(sep)]
    headers = []
    units = {}
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
        headers = headers[:-1]

    units = dgutils.sanitize_units(units)
    return headers, units


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
    vals["uts"] = DataArray(data=utslist, dims=["uts"])
    vals.attrs["fulldate"] = False
    return vals
