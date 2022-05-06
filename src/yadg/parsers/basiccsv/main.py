import logging
import json
import uncertainties as uc
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from typing import Callable
from pydantic import BaseModel
from ... import dgutils

logger = logging.getLogger(__name__)


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

    This is the main worker function of ``basiccsv``, but can be re-used by any other
    parser that needs to process tabular data.

    .. _processing_convert:

    This function processes the ``"calib"`` parameter, which should be a :class:`(dict)`
    in the following format:

    .. code-block:: yaml

      - new_name:     !!str    # derived entry name
        - old_name:   !!str    # raw header name
          - calib: {}          # calibration specification
          fraction:   !!float  # coefficient for linear combinations of old_name
        unit:         !!str    # unit of new_name

    The syntax of the calibration specification is detailed in
    :func:`yadg.dgutils.calib.calib_handler`.

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
        quantities. Arbitrary linear combinations of ``headers`` are possible. See
        :ref:`the above section<processing_convert>` for the specification.

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

    assert all([key in units for key in headers]), (
        f"process_row: Not all entries in provided 'headers' are present "
        f"in provided 'units': {headers} vs {units.keys()}"
    )

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
            val, sig = tuple_fromstr(columns[ci])
            unit = units[header]
            element["raw"][header] = {"n": val, "s": sig, "u": unit}
            raw[header] = (val, sig)
        except ValueError:
            element["raw"][header] = columns[ci]

    # Process calib
    for newk, spec in calib.items():
        y = uc.ufloat(0, 0)
        oldu = " "
        for oldk, v in spec.items():
            if oldk in der:
                dy = dgutils.calib_handler(
                    der[oldk],
                    v.get("calib", None),
                )
                y += dy * v.get("fraction", 1.0)
                oldu = element["derived"][oldk]["u"]
            elif oldk in raw:
                dy = dgutils.calib_handler(
                    uc.ufloat(*raw[oldk]),
                    v.get("calib", None),
                )
                y += dy * v.get("fraction", 1.0)
                oldu = element["raw"][oldk]["u"]
            elif oldk == "unit":
                pass
            else:
                logger.warning(
                    "process_row: Supplied key '%s' is neither a 'raw' "
                    "nor a 'derived' key.",
                    oldk,
                )
        if "derived" not in element:
            element["derived"] = dict()
        element["derived"][newk] = {"n": y.n, "s": y.s, "u": spec.get("unit", oldu)}
        der[newk] = y
    return element


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
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
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.dataschema_4_1.parameters.BasicCSV`.

    Returns
    -------
    (data, metadata, fulldate): tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned by the basiccsv parser. The full date might not be returned, eg.
        when only time is specified in columns.

    """
    # Process calfile and convert into calib
    if parameters.calfile is not None:
        with open(parameters.calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if parameters.convert is not None:
        calib.update(parameters.convert)

    # Load file, extract headers and get timestamping function
    with open(fn, "r", encoding=encoding) as infile:
        # This decode/encode is done to account for some csv files that have a BOM
        # at the beginning of each line.
        lines = [i.encode().decode(encoding) for i in infile.readlines()]
    assert len(lines) >= 2
    headers = [header.strip() for header in lines[0].split(parameters.sep)]
    datecolumns, datefunc, fulldate = dgutils.infer_timestamp_from(
        headers=headers, spec=parameters.timestamp, timezone=timezone
    )

    # Populate units
    units = parameters.units
    if units is None:
        units = {}
        _units = [column.strip() for column in lines[1].split(parameters.sep)]
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
    data = []
    for line in lines[si:]:
        element = process_row(
            headers,
            line.split(parameters.sep),
            units,
            datefunc,
            datecolumns,
            calib=calib,
        )
        element["fn"] = str(fn)
        data.append(element)
    return data, None, fulldate
