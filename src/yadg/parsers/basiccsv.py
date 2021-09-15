import os
from helpers import dateutils
import datetime
import logging

def _infer_timestamp_from(headers):
    if "uts" in headers:
        return ([headers.index("uts")], None)
    elif "timestamp" in headers:
        return ([headers.index("timestamp")], "%Y-%m-%d %H:%M:%S")
    elif "date" in headers:
        if "time" in headers:
            return ([headers.index("date"), headers.index("time")],
                    ["%Y-%m-%d", "%H:%M:%S"])
        else:
            return ([headers.index("date")], "%Y-%m-%d")
    elif len(set(["day", "month", "year"], headers)) == 3:
        cols = [headers.index("day"), headers.index("month"), headers.index("year")]
        forms = ["%d", "%m", "%Y"]
        if "hour" in headers:
            cols.append(headers.index("hour"))
            forms.append("%H")
            if "minute" in headers:
                cols.append(headers.index("minute"))
                forms.append("%M")
                if "second" in headers:
                    cols.append(headers.index("second"))
                    forms.append("%S")
        return (cols, forms)
    logging.error("Timestamp could not be deduced.")

def _compute_timestamp_from(values, formats):
    if len(values) == 1:
        if formats is None:
            return float(values[0])
        else:
            return datetime.datetime.strptime(values[0], formats)

def process(fn, sep = ",", rtol = 0.001, atol = 0, 
            sigma = {}, units = None, **kwargs):
    """
    A basic csv parser.

    This parser processes a csv file. The header of the csv file consists of one
    or two lines, with the column headers in the first line and the units in the
    second. The parser also attempts to combine columns to produce a timestamp, 
    and save all other columns as floats or strings. The default uncertainty is 
    0.1%.

    Parameters
    ----------
    fn : string
        File to process
    
    sep : string, optional
        Separator to use. Default is "," for csv.

    rtol : float, optional
        The default relative uncertainty accross all float values. A conservative
        value of 0.1% is used as default.
    
    atol : float, optional
        The default absolute uncertainty accross all float values. By default set
        to 0, i.e. the rtol is always used.

    sigma : dict, optional
        Column-specific `atol` and `rtol` values can be supplied here.
    
    units : dict, optional
        Column-specific unit specification. If present, 2nd line is treated as
        data. If omitted, 2nd line is treated as units.

    """
    
    with open(fn, "r") as infile:
        lines = infile.readlines()
    assert len(lines) >= 2
    headers = [header.strip() for header in lines[0].split(sep)]

    datecolumns, dateformat = _infer_timestamp_from(headers)
    if units is None:
        units = {}
        _units = [column.strip() for column in lines[1].split(sep)]
        for header in headers:
            units[header] = _units.pop(0)
        si = 2
    else:
        for header in headers:
            if header not in units:
                logging.warning(f"Using implicit unit '-' for {header}.")
                units["header"] = "-"
            elif units["header"] == "":
                logging.info(f"Converting unit ' ' to '-' for {header}.")
                units["header"] = "-"
        si = 1
    
    data = []
    for line in lines[si:]:
        element = {}
        columns = [column.strip() for column in line.split(sep)]
        element["uts"] = _compute_timestamp_from([columns[i] for i in datecolumns], dateformat)
        for header in headers:
            ci = headers.index(header)
            if ci in datecolumns:
                continue
            try:
                _val = float(columns[ci])
                _tols = sigma.get(header, {"rtol": rtol, "atol": atol})
                _sigma = max(abs(_val * _tols["rtol"]), _tols["atol"])
                _unit = units.get(header)
                element[header] = [_val, _sigma, _unit]
            except ValueError:
                element[header] = columns[ci]
        data.append(element)
    return data
