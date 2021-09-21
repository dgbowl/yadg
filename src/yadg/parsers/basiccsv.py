from helpers import dateutils
import logging

def process(fn, sep = ",", atol = 0, rtol = 0.001, sigma = {},
            units = None, timestamp = None, **kwargs):
    """
    A basic csv parser.

    This parser processes a csv file. The header of the csv file consists of one
    or two lines, with the column headers in the first line and the units in the
    second. The parser also attempts to parse column names to produce a timestamp, 
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

    timestamp : dict, optional
        Specification for timestamping. Allowed keys are "date", "time",
        "timestamp", "uts". The entries can be column indices (int), or tuples
        consisting  of a column index (int), and format (str).
    """
    with open(fn, "r") as infile:
        lines = infile.readlines()
    assert len(lines) >= 2
    headers = [header.strip() for header in lines[0].split(sep)]

    datecolumns, datefunc = dateutils._infer_timestamp_from(headers, spec = timestamp)
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
        element["uts"] = datefunc(*[columns[i] for i in datecolumns])
        for header in headers:
            ci = headers.index(header)
            if ci in datecolumns:
                continue
            try:
                _val = float(columns[ci])
                _tols = sigma.get(header, {"rtol": rtol, "atol": atol})
                _sigma = max(abs(_val * _tols.get("rtol", 0)), _tols.get("atol", 0))
                _unit = units.get(header)
                element[header] = [_val, _sigma, _unit]
            except ValueError:
                element[header] = columns[ci]
        data.append(element)
    return data, None, None
