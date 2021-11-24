import datetime
import logging
import re
import math
from typing import Union

from yadg.dgutils.dateutils import ole_to_uts
from eclabfiles.mpr import parse_mpr
from eclabfiles.mpt import parse_mpt


version = "1.0.dev1"


def _process_datapoints(
    datapoints: list[dict],
    acquisition_start: Union[float, str],
    fn: str,
) -> list[dict]:
    """Processes the datapoints from parsed `.mpr` or `.mpt` files.

    The data from EC-Lab does not yet contain uncertainties, the units
    need to be parsed and the POSIX timestamp is missing at every
    datapoint.

    Parameters
    ----------
    datapoints
        The datapoints as parsed from an EC-Lab file. The `.mpr` parser
        writes them at parsed_mpr[i]['data']['datapoints'] while they
        are at parsed_mpt['data'] from the `.mpt` parser.

    acquisition_start
        Timestamp of when the data acquisition started. This is found in
        the log module data of `.mpr` files in OLE format (float) and in
        the settings header of `.mpt` as a string.

    Returns
    -------
    list[dict]
        The processed datapoints.

    """
    if isinstance(acquisition_start, str):
        # Parse timestamp. Time format annoyingly changes.
        start = None
        time_formats = [
            "%m/%d/%Y %H:%M:%S",
            "%m.%d.%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S.%f",
        ]
        for time_format in time_formats:
            try:
                start = datetime.datetime.strptime(
                    acquisition_start, time_format
                ).timestamp()
                break
            except ValueError:
                logging.debug(
                    f"_process_datapoints: Time format {time_format} "
                    f"does not apply. Trying next option..."
                )
        if start is None:
            raise NotImplementedError(
                f"Time format for {acquisition_start} not implemented."
            )
    elif isinstance(acquisition_start, float):
        # OLE timestamp from `.mpr` files.
        start = ole_to_uts(acquisition_start)
    else:
        raise TypeError(f"Unknown start time type: {type(acquisition_start)}")
    for datapoint in datapoints:
        # Calculate UTS for the datapoint.
        offset = datapoint["raw"]["time/s"]
        time = start + offset
        # Separate the unit from every column type.
        for key, value in datapoint["raw"].items():
            unit = "-"
            if key not in {"ox/red"}:
                split = key.split("/")
                if len(split) > 1:
                    unit = split[-1]
            # Using the unit of least precision as a measure of
            # uncertainty for now, i.e the spacing between two
            # consecutive floats.
            datapoint["raw"][key] = {"n": value, "s": math.ulp(value), "u": unit}
        datapoint["uts"] = time
        datapoint["fn"] = fn
    return datapoints


def _process_mpr(fn: str) -> tuple[list, dict, dict]:
    """Processes an EC-Lab `.mpr` file."""
    datapoints = []
    meta = {}
    common = {}
    mpr = parse_mpr(fn)
    for module in mpr:
        name = module["header"]["short_name"]
        if name == "VMP Set   ":
            meta["settings"] = module["data"].copy()
            common["params"] = meta["settings"].pop("params")
        elif name == "VMP data  ":
            datapoints = [{"raw": point} for point in module["data"]["datapoints"]]
        elif name == "VMP LOG   ":
            meta["log"] = module["data"]
            acquisition_start = module["data"]["ole_timestamp"]
            datapoints = _process_datapoints(datapoints, acquisition_start, fn)
        elif name == "VMP loop  ":
            meta["loops"] = module["data"]
    # TODO: The right params common should be associated with the data
    # points. This can be done through the length of params and the Ns
    # column.
    return datapoints, meta, common


def _process_mpt(fn: str) -> tuple[list, dict, dict]:
    """Processes an EC-Lab `.mpt` file."""
    datapoints = []
    meta = {}
    common = {}
    mpt = parse_mpt(fn)
    acquisition_start = datetime.datetime.strftime(
        datetime.datetime.now(), r"%m/%d/%Y %H:%M:%S"
    )
    if "settings" in mpt["header"]:
        meta["settings"] = mpt["header"].copy()
        common["params"] = meta["settings"].pop("params")
        acquisition_start_match = re.search(
            r"Acquisition started on : (?P<val>.+)",
            "\n".join(mpt["header"]["settings"]),
        )
        acquisition_start = acquisition_start_match["val"]
        logging.debug(f"_process_mpt: Start of acquisition: {acquisition_start}")
    if "loops" in mpt["header"]:
        meta["loops"] = mpt["header"]["loops"]
    # TODO: The right params common should be associated with the data
    # points. This can be done through the length of params and the Ns
    # column.
    datapoints = [{"raw": point} for point in mpt["datapoints"]]
    datapoints = _process_datapoints(datapoints, acquisition_start, fn)
    return datapoints, meta, common


def process(
    fn: str,
    encoding: str = "windows-1252",
    timezone: str = "localtime",
    filetype: str = None,
) -> tuple[list, dict, dict]:
    """Processes an EC-Lab electrochemistry data file.

    # TODO: Implement encoding and timezone support.

    """
    if filetype is None:
        filetype = fn.split(".")[-1]
    if filetype == "mpr":
        timesteps, meta, common = _process_mpr(fn)
    elif filetype == "mpt":
        timesteps, meta, common = _process_mpt(fn)
    return timesteps, meta, common
