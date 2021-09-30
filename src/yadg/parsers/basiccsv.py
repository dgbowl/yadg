import logging
from uncertainties import ufloat
import dgutils

def process(fn: str, sep: str = ",", atol: float = 0.0, rtol: float = 0, 
            sigma: dict = {}, units: dict = None, timestamp: dict = None,
            convert: dict = None, **kwargs):
    """
    A basic csv parser.

    This parser processes a csv file. The header of the csv file consists of one
    or two lines, with the column headers in the first line and the units in the
    second. The parser also attempts to parse column names to produce a timestamp, 
    and save all other columns as floats or strings. The default uncertainty is 
    0.1%.

    Parameters
    ----------
    fn
        File to process
    
    sep
        Separator to use. Default is "," for csv.

    atol
        The default absolute uncertainty accross all float values in csv columns. 
        By default set to 0.

    rtol
        The default relative uncertainty accross all float values in csv columns. 
        By default set to 0.

    sigma
        Column-specific ``atol`` and ``rtol`` values can be supplied here.
    
    units
        Column-specific unit specification. If present, 2nd line is treated as
        data. If omitted, 2nd line is treated as units.

    timestamp
        Specification for timestamping. Allowed keys are ``"date"``, ``"time"``,
        ``"timestamp"``, ``"uts"``. The entries can be column indices 
        :class:`(int)`, or a ::class:`tuple(int, str)` consisting of a column 
        index :class:`(int)`, and format :class:`(str)`.
    
    convert
        Specification for column conversion. Each entry will form a new datapoint,
        must contain a valid ``"header"`` entry and a ``"calib"`` specification.

    """
    metadata = {
        "fn": str(fn)
    }
    with open(fn, "r") as infile:
        lines = infile.readlines()
    assert len(lines) >= 2
    headers = [header.strip() for header in lines[0].split(sep)]

    datecolumns, datefunc = dgutils.infer_timestamp_from(headers, spec = timestamp)
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
                _tols = sigma.get(header, {})
                _sigma = max(abs(_val * _tols.get("rtol", rtol)), _tols.get("atol", atol))
                _unit = units.get(header)
                element[header] = [_val, _sigma, _unit]
                if convert is not None:
                    for nk, spec in convert.items():
                        if header == spec["header"]:
                            y = dgutils.calib_handler(ufloat(_val, _sigma), spec["calib"])
                            element[nk] = [y.n, y.s, spec.get("unit", "-")]
            except ValueError:
                element[header] = columns[ci]
        data.append(element)
    return data, metadata, None
