import logging
import json

from yadg.parsers.flowdata import drycal
import yadg.dgutils

version = "4.0.0"

def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    filetype: str = "drycal",
    convert: dict = None,
    calfile: str = None,
    date: str = None,
) -> tuple[list, dict, dict]:
    """
    Flow meter data processor

    This parser processes flow meter data.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    filetype
        Whether a rtf, csv, or txt file is to be expected. When `None`, the suffix of
        the file is used to determine the file type.

    convert
        Specification for column conversion. The `key` of each entry will form a new
        datapoint in the ``"derived"`` :class:`(dict)` of a timestep. The elements within
        each entry must either be one of the ``"header"`` fields, or ``"unit"`` :class:`(str)`
        specification. See :ref:`processing convert<processing_convert>` for more info.

    calfile
        ``convert``-like functionality specified in a json file.
    
    date
        An optional date argument, required for parsing DryCal files. Otherwise the date
        is parsed from ``fn``.

    Returns
    -------
    (data, metadata, common) : tuple[list, None, None]
        Tuple containing the timesteps, metadata, and common data.

    """
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if convert is not None:
        calib.update(convert)
    
    metadata = {}

    if filetype == "drycal":
        if date is None:
            date = fn
        date = yadg.dgutils.date_from_str(date)
        assert date is not None, "Log starting date must be specified."
        
        if "flow" not in calib:
            logging.info("flowdata: adding default 'DryCal' -> 'flow' conversion")
            calib["flow"] = {"DryCal": {"calib": {"linear": {"slope": 1.0}}}}

        if fn.endswith("rtf"):
            ts, meta = drycal.rtf(fn, date, encoding, timezone, calib)
        elif fn.endswith("csv"):
            ts, meta = drycal.sep(fn, date, ",", encoding, timezone, calib)
        elif fn.endswith("txt"):
            ts, meta = drycal.sep(fn, date, "\t", encoding, timezone, calib)

    metadata.update(meta)

    return ts, metadata, None
