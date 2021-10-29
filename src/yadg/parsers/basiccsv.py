import logging
import json
from uncertainties import ufloat_fromstr, ufloat
import yadg.dgutils
from typing import Callable

version = "1.0.dev1"


def tols_from(
    headers: list, sigma: dict = {}, atol: float = 0.0, rtol: float = 0.0
) -> dict:
    """
    Uncertainty helper function.

    Given a list of ``headers``, creates a dictionary where each key is an element of
    ``headers``, and the values are atol and rtol from the corresponding key in ``sigma``,
    or the default values provided as parameters
    """
    # Populate tols from sigma, atol, rtol
    tols = dict()
    for header in headers:
        tols[header] = {
            "atol": sigma.get(header, {}).get("atol", atol),
            "rtol": sigma.get(header, {}).get("rtol", rtol),
        }
    return tols


def process_row(
    headers: list,
    items: list,
    units: dict,
    datefunc: Callable,
    datecolumns: list,
    calib: dict = {},
) -> dict:
    """
    A function that processes a row of a table.

    This is the main worker function of basiccsv, but can be re-used by any other parser
    that needs to process tabular data.

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

    calib
        Specification for converting raw data in ``headers`` and ``items`` to other
        quantities Arbitrary linear combinations of ``headers`` are possible.

    Returns
    -------
    element: dict
        A result dictionary, containing the keys ``"uts"`` with a timestamp, ``"raw"`` for
        all raw data present in the headers, and ``"derived"`` for any data processes via ``calib``.

    """
    assert len(headers) == len(
        items
    ), f"process_row: Length mismatch between provided headers: {headers} and  provided items: {items}."

    assert all(
        [key in units for key in headers]
    ), f"process_row: Not all entries in provided 'headers' are present in provided 'units': {headers} vs {units.keys()}"

    raw = dict()
    der = dict()
    element = {"raw": dict()}
    columns = [column.strip() for column in items]

    # Process raw data, assign sigma and units
    element["uts"] = datefunc(*[columns[i] for i in datecolumns])
    for header in headers:
        ci = headers.index(header)
        if ci in datecolumns:
            continue
        try:
            val = ufloat_fromstr(columns[ci])
            unit = units[header]
            element["raw"][header] = {"n": val.n, "s": val.s, "u": unit}
            raw[header] = val
        except ValueError:
            element["raw"][header] = columns[ci]

    # Process calib
    for newk, spec in calib.items():
        y = ufloat(0, 0)
        for oldk, v in spec.items():
            if oldk in der:
                dy = yadg.dgutils.calib_handler(der[oldk], v.get("calib", None))
                y += dy * v.get("fraction", 1.0)
            elif oldk in raw:
                dy = yadg.dgutils.calib_handler(raw[oldk], v.get("calib", None))
                y += dy * v.get("fraction", 1.0)
            elif oldk == "unit":
                pass
            else:
                logging.warning(
                    f"process_row: Supplied key '{oldk}' is neither a 'raw' nor a 'derived' key."
                )
        if "derived" not in element:
            element["derived"] = dict()
        element["derived"][newk] = {"n": y.n, "s": y.s, "u": spec.get("unit", "-")}
        der[newk] = y
    return element


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    sep: str = ",",
    units: dict = None,
    timestamp: dict = None,
    convert: dict = None,
    calfile: str = None,
) -> tuple[list, dict, None]:
    """
    A basic csv parser.

    This parser processes a csv file. The header of the csv file consists of one or two
    lines, with the column headers in the first line and the units in the second. The
    parser also attempts to parse column names to produce a timestamp, and save all other
    columns as floats or strings. The default uncertainty is 0.0.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    sep
        Separator to use. Default is "," for csv.

    units
        Column-specific unit specification. If present, even if empty, 2nd line is
        treated as data. If omitted, 2nd line is treated as units.

    timestamp
        Specification for timestamping. Allowed keys are ``"date"``, ``"time"``,
        ``"timestamp"``, ``"uts"``. The entries can be ``"index"`` :class:`(list[int])`,
        containing the column indices, and ``"format"`` :class:`(str)` with the format
        string to be used to parse the date. See :func:`yadg.dgutils.dateutils.infer_timestamp_from`
        for more info.

    convert
        Specification for column conversion. The `key` of each entry will form a new
        datapoint in the ``"derived"`` :class:`(dict)` of a timestep. The elements within
        each entry must either be one of the ``"header"`` fields, or ``"unit"``
        :class:`(str)` specification. See :func:`yadg.parsers.basiccsv.process_row`
        for more info.

    calfile
        ``convert``-like functionality specified in a json file.

    Returns
    -------
    (data, metadata, common) : tuple[list, None, None]
        Tuple containing the timesteps, metadata, and common data.

    """
    # Process calfile and convert into calib
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if convert is not None:
        calib.update(convert)

    # Load file, extract headers and get timestamping function
    with open(fn, "r", encoding=encoding) as infile:
        # This decode/encode is done to account for some csv files that have a BOM at the beginning of each line.
        lines = [i.encode().decode(encoding) for i in infile.readlines()]
    assert len(lines) >= 2
    headers = [header.strip() for header in lines[0].split(sep)]
    datecolumns, datefunc = yadg.dgutils.infer_timestamp_from(
        headers=headers, spec=timestamp, timezone=timezone
    )

    # Populate units
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

    # Process rows
    data = []
    for line in lines[si:]:
        element = process_row(headers, line.split(sep), units, datefunc, datecolumns, calib=calib)
        element["fn"] = str(fn)
        data.append(element)
    return data, None, None
