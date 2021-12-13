"""
File parser for DryCal log files, including converted documents (rtf) and tabulated
exports (txt, csv).

The DryCal files only contain the timestamps of the datapoints, not the date. Therefore,
the date has to be supplied either using the ``date`` argument in parameters, or is 
parsed from the prefix of the filename.

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""

from yadg.parsers.basiccsv import process_row
from striprtf.striprtf import rtf_to_text
import yadg.dgutils


def rtf(
    fn: str,
    date: float,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    calib: dict = {},
) -> tuple[list, dict]:
    """
    RTF version of the drycal parser.

    This is intended to parse legacy drycal DOC files, which have been converted to RTF
    using other means.

    Parameters
    ----------
    fn
        Filename to parse.

    date
        A unix timestamp float corresponding to the day (or other offset) to be added to
        each line in the measurement table.

    encoding
        Encoding to use for parsing ``fn``.

    calib
        A calibration spec.

    Returns
    -------
    (timesteps, metadata, None): tuple[list, dict, None]
        A standard data - metadata - common data output tuple.
    """
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
    datecolumns, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"time": {"index": 4, "format": "%I:%M:%S %p"}}, timezone=timezone
    )

    # Correct each ts by provided date
    timesteps = []
    for r in data:
        ts = process_row(headers[1:], r[1:], units, datefunc, datecolumns, calib=calib)
        ts["uts"] += date
        ts["fn"] = fn
        timesteps.append(ts)

    return timesteps, metadata


def sep(
    fn: str,
    date: float,
    sep: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    calib: dict = {},
) -> tuple[list, dict]:
    """
    Generic drycal parser, using ``sep`` as separator string.

    This is intended to parse other export formats from DryCal, such as txt and csv files.

    Parameters
    ----------
    fn
        Filename to parse.

    date
        A unix timestamp float corresponding to the day (or other offset) to be added to
        each line in the measurement table.

    sep
        The separator character used to split lines in ``fn``.

    encoding
        Encoding to use for parsing ``fn``.

    calib
        A calibration spec.

    Returns
    -------
    (timesteps, metadata, None): tuple[list, dict, None]
        A standard data - metadata - common data output tuple.
    """
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
    datecolumns, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"time": {"index": 4, "format": "%H:%M:%S"}}, timezone=timezone
    )

    # Correct each ts by provided date
    timesteps = list()
    for r in data:
        ts = process_row(headers[1:], r[1:], units, datefunc, datecolumns, calib=calib)
        ts["uts"] += date
        ts["fn"] = str(fn)
        timesteps.append(ts)

    return timesteps, metadata


def drycal_table(lines: list, sep: str = ",") -> tuple[list, dict, list]:
    """
    DryCal table-processing function.

    Given a table with headers and units in the first line, and data in the following
    lines, this function returns the headers, units, and data extracted from the table.
    The returned values are always of :class:`(str)` type, any post-processing is done
    in the calling routine.

    Parameters
    ----------
    lines
        A list containing the lines to be parsed

    sep
        The separator string used to split each line into individual items

    Returns
    -------
    (headers, units, data): tuple[list, dict, list]
        A tuple of a list of the stripped headers, dictionary of header-unit key-value
        pairs, and a list of lists containing the rows of the table.
    """
    items = [i.strip() for i in lines[0].split(sep)]
    headers = []
    units = {}
    data = []
    for item in items:
        for rs in [". ", " "]:
            parts = item.split(rs)
            if len(parts) == 2:
                break
        headers.append(parts[0])
        if len(parts) == 2:
            units[parts[0]] = parts[1]
        else:
            units[parts[0]] = "-"
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
    return headers, units, data
