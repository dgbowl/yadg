"""
Handles the reading and processing of any tabular files, as long as the first line
contains the column headers. The columns of the table must be separated using a
separator such as ``,``, ``;``, or ``\\t``.

.. note::

    By default, the second line of the file should contain the units. Alternatively,
    the units can be supplied using extractor parameters, in which case the second line
    is considered to be data.

Since ``yadg-5.0``, the **basic.csv** extractor handles sparse tables (i.e. tables with
missing data) by back-filling empty cells with ``np.NaNs``.

The **basic.csv** extractor attempts to deduce the timestamps from the column headers,
using :func:`yadg.dgutils.dateutils.infer_timestamp_from`. Alternatively, the column(s)
containing the timestamp data and their format can be provided using extractor
parameters.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Basic_csv

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:            !!float               # Unix timestamp
      data_vars:
        {{ headers }}:  (uts)                 # Populated from file headers

Metadata
````````
No metadata is extracted.

.. codeauthor::
    Peter Kraus

"""

import logging
from pydantic import BaseModel
from babel.numbers import parse_decimal
from datatree import DataTree
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from typing import Callable


from yadg import dgutils


logger = logging.getLogger(__name__)


def process_row(
    headers: list,
    items: list,
    datefunc: Callable,
    datecolumns: list[int],
    locale: str = "en_GB",
) -> tuple[dict, dict]:
    """
    A function that processes a row of a table.

    This is the main worker function of :mod:`basic.csv` module, but is often
    re-used by any other parser that needs to process tabular data.

    Parameters
    ----------
    headers
        A list of headers of the table.

    items
        A list of values corresponding to the headers. Must be the same length as
        headers.

    datefunc
        A function that will generate ``uts`` given a list of values.

    datecolumns
        Column indices that need to be passed to ``datefunc`` to generate uts.

    Returns
    -------
    vals, devs
        A tuple of result dictionaries, with the first element containing the values
        and the second element containing the uncertainties of the values.

    """
    if len(headers) != len(items):
        raise RuntimeError(
            f"Length mismatch between provided headers {headers!r} and items {items!r}."
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
            val, dev = tuple_fromstr(str(parse_decimal(columns[ci], locale=locale)))
            vals[header] = val
            devs[header] = dev
        except ValueError:
            vals[header] = columns[ci]

    return vals, devs


def extract(
    *,
    fn: str,
    encoding: str,
    locale: str,
    timezone: str,
    parameters: BaseModel,
    **kwargs: dict,
) -> DataTree:
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
                logger.warning(f"Using implicit dimensionless unit ' ' for {header!r}")
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
            locale=locale,
        )
        dgutils.append_dicts(vals, devs, data_vals, meta_vals, fn, li)

    return DataTree(dgutils.dicts_to_dataset(data_vals, meta_vals, units, fulldate))
