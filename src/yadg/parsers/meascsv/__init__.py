"""
This parser handles the reading and processing of the legacy log files created by
the LabView interface for the MCPT instrument. These files contain information about
the timestamp, temperatures, and inlet / process flows.

.. admonition:: DEPRECATED in ``yadg-4.0``

    As of ``yadg-4.0``, this parser is deprecated and should not be used for new data.
    Please consider switching to the :mod:`~yadg.parsers.basiccsv` parser.

Usage
`````
Available since ``yadg-3.0``. Deprecated since ``yadg-4.0``. The parser supports the
following parameters:

.. _yadg.parsers.meascsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.MeasCSV

.. _parsers_meascsv_provides:

Schema
``````
The parser is used to extract all of the tabular data in the input file, storing
them in the same format as :mod:`~yadg.parsers.basiccsv`, using the column headers
as keys.

"""

import logging
from pydantic import BaseModel
from zoneinfo import ZoneInfo
from ..basiccsv.main import process_row, append_dicts, dicts_to_dataset
from ... import dgutils
import xarray as xr

logger = logging.getLogger(__name__)


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    parameters: BaseModel,
    **kwargs: dict,
) -> xr.Dataset:
    """
    Legacy MCPT measurement log parser.

    This parser is included to maintain parity with older schemas and datagrams.
    It is essentially a wrapper around :func:`yadg.parsers.basiccsv.main.process_row`.

    .. admonition:: DEPRECATED in ``yadg-4.0``

        For new applications, please use the :mod:`~yadg.parsers.basiccsv` parser.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_5_0.step.MeasCSV`.

    Returns
    -------
    :class:`xarray.Dataset`
        A :class:`xarray.Dataset` containing the timesteps, metadata, and full date tag. No
        metadata is returned. The full date is always provided in :mod:`~yadg.parsers.meascsv`
        compatible files.

    """
    logger.warning("This parser is deprecated. Please switch to 'basiccsv'.")

    with open(fn, "r", encoding=encoding) as infile:
        lines = [i.strip() for i in infile.readlines()]

    headers = [i.strip() for i in lines.pop(0).split(";")]

    for hi, header in enumerate(headers):
        if "/" in header:
            logger.warning("Replacing '/' for '_' in header '%s'.", header)
            headers[hi] = header.replace("/", "_")

    _units = [i.strip() for i in lines.pop(0).split(";")]
    units = {}
    for h in headers:
        units[h] = _units.pop(0)

    units = dgutils.sanitize_units(units)

    datecolumns, datefunc, fulldate = dgutils.infer_timestamp_from(
        spec=parameters.timestamp,
        timezone=timezone,
    )

    # Process rows
    data_vals = {}
    meta_vals = {"_fn": []}
    for li, line in enumerate(lines):
        vals, devs = process_row(
            headers,
            line.split(";"),
            datefunc,
            datecolumns,
        )
        append_dicts(vals, devs, data_vals, meta_vals, fn, li)

    return dicts_to_dataset(data_vals, meta_vals, units, fulldate)
