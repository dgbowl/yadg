import logging
import json
from uncertainties import ufloat
import dgutils
from typing import Callable

def process_row(headers: list, items: list, units: dict, datefunc: Callable, 
                datecolumns: list, atol: float = 0.0, rtol: float = 0.0, 
                sigma: dict = {}, calib: dict = {}) -> dict:
    """
    A function that processes a row of a table.

    This is the main worker function of basiccsv, but can be re-used by any 
    other parser that needs to process tabular data.

    Parameters
    ----------
    headers
        A list of headers of the table.
    
    items
        A list of values corresponding to the headers. Must be the same length
        as headers.
    
    units
        A dict for looking up the units corresponding to a certain header.
    
    datefunc
        A function that will generate ``uts`` given a list of values.
    
    datecolumns
        Column indices that need to be passed to ``datefunc`` to generate uts.
    
    atol
        Absolute uncertainty for all floating-point values.
    
    rtol
        Relative uncertainty for all floating-point values.
    
    sigma
        Per-header specification of ``atol`` and ``rtol``.

    calib
        Specification for converting raw data in ``headers`` and ``items`` to 
        other quantities. Arbitrary linear combinations of ``headers`` are 
        possible.
    
    Returns
    -------
    element: dict
        A result dictionary, containing the keys ``"uts"`` with a timestamp, 
        ``"raw"`` for all raw data present in the headers, and ``"derived"``
        for any data processes via ``calib``.

    """
    assert len(headers) == len(items), \
        f"process_row: Length mismatch between provided headers: {headers} and" \
        f" provided items: {items}."

    element = {"raw": dict()}
    columns = [column.strip() for column in items]
    element["uts"] = datefunc(*[columns[i] for i in datecolumns])
    for header in headers:
        ci = headers.index(header)
        if ci in datecolumns:
            continue
        try:
            _val = float(columns[ci])
            _tols = sigma.get(header, {})
            _sigma = max(abs(_val * _tols.get("rtol", rtol)), _tols.get("atol", atol))
            _unit = units[header]
            element["raw"][header] = [_val, _sigma, _unit]
        except ValueError:
            element["raw"][header] = columns[ci]
    for nk, spec in calib.items():
        y = ufloat(0, 0)
        for ck, v in spec.items():
            if ck not in headers:
                if ck != "unit":
                    logging.warning(f"{ck}")
            else:
                dy = dgutils.calib_handler(ufloat(*element["raw"][ck]), v.get("calib", None))
                y += dy * v.get("fraction", 1.0)
        if "derived" not in element:
            element["derived"] = dict()
        element["derived"][nk] = [y.n, y.s, spec.get("unit", "-")]
    return element

def process(fn: str, encoding: str = "utf-8", sep: str = ",", 
            atol: float = 0.0, rtol: float = 0.0, sigma: dict = {}, 
            units: dict = None, timestamp: dict = None,
            convert: dict = None, calfile: str = None, 
            **kwargs) -> tuple[list, dict, None]:
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
    
    encoding
        Encoding of ``fn``, by default "utf-8".

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
    
    calfile
        ``convert``-like functionality specified in a json file.

    """
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if convert is not None:
        calib.update(convert)
    metadata = {}
    with open(fn, "r", encoding = encoding) as infile:
        lines = [i.encode().decode(encoding) for i in infile.readlines()]
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
                units[header] = "-"
            elif units[header] == "":
                logging.info(f"Converting unit ' ' to '-' for {header}.")
                units[header] = "-"
        si = 1
    data = []
    for line in lines[si:]:
        element = process_row(headers, line.split(sep), units,
                              datefunc, datecolumns, atol, rtol,
                              sigma, calib)
        element["fn"] = str(fn)
        data.append(element)
    return data, metadata, None
