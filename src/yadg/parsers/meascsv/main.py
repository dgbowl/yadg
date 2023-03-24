import logging
from pydantic import BaseModel
from zoneinfo import ZoneInfo
from ..basiccsv.main import process_row, append_dicts, dicts_to_datasets
from ... import dgutils
from datatree import DataTree

logger = logging.getLogger(__name__)


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
) -> DataTree:
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
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.MeasCSV`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned. The full date is always provided in meascsv-compatible files.

    """
    logger.warning("This parser is deprecated. Please switch to 'basiccsv'.")

    with open(fn, "r", encoding=encoding) as infile:
        lines = [i.strip() for i in infile.readlines()]

    headers = [i.strip() for i in lines.pop(0).split(";")]
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

    return dicts_to_datasets(data_vals, meta_vals, units, fulldate)
