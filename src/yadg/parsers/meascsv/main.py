import json
import logging
from pydantic import BaseModel
from uncertainties import ufloat
from ..basiccsv.main import process_row
from ... import dgutils

logger = logging.getLogger(__name__)


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
    """
    Legacy MCPT measurement log parser.

    This parser is included to maintain parity with older schemas and datagrams.
    It is essentially a wrapper around :func:`yadg.parsers.basiccsv.process_row`.
    For new applications, please use the `basiccsv` parser.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.parameters.dataschema_4_1.MeasCSV`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned. The full date is always provided in meascsv-compatible files.

    """
    logger.warning("This parser is deprecated. Please switch to 'basiccsv'.")

    if parameters.calfile is not None:
        with open(parameters.calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if parameters.convert is not None:
        calib.update(parameters.convert)

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
    timesteps = []
    for line in lines:
        ts = process_row(
            headers, line.split(";"), units, datefunc, datecolumns, calib=calib
        )
        ts["fn"] = str(fn)

        if "derived" in ts:
            xin = {}
            total = ufloat(0, 0)
            for mfc in ts["derived"].keys():
                if mfc.startswith("flow") or mfc.startswith("T"):
                    continue
                xin[mfc] = ufloat(ts["derived"][mfc]["n"], ts["derived"][mfc]["s"])
                total += xin[mfc]
            if xin != {}:
                ts["derived"]["xin"] = {}
                for species in xin:
                    x = xin[species] / total
                    ts["derived"]["xin"][species] = {"n": x.n, "s": x.s, "u": " "}
        timesteps.append(ts)
    return timesteps, None, fulldate
