import datetime
import logging
import os
import re
from typing import Union

from dgutils.dateutils import ole_to_datetime
from eclabfiles.mpr import parse_mpr
from eclabfiles.mpt import parse_mpt


def _process_datapoints(
    datapoints: list[dict],
    acquisition_start: Union[float, str],
    **kwargs
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
            '%m/%d/%Y %H:%M:%S',
            '%m.%d.%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S.%f',
        ]
        for time_format in time_formats:
            try:
                start = datetime.datetime.strptime(
                    acquisition_start, time_format)
                break
            except ValueError:
                logging.debug(
                    "Time format %s does not apply. Trying next option...",
                    time_format)
        if start is None:
            raise NotImplementedError(
                f"Time format for {acquisition_start} not implemented.")
    elif isinstance(acquisition_start, float):
        # OLE timestamp from `.mpr` files.
        start = ole_to_datetime(acquisition_start)
    else:
        raise TypeError(f"Unknown start time type: {type(acquisition_start)}")
    for datapoint in datapoints:
        # Calculate UTS for the datapoint.
        offset = datetime.timedelta(seconds=datapoint['time/s'])
        time = start + offset
        # Separate the unit from every column type.
        for key, value in datapoint.items():
            split = key.split('/')
            del split[0]
            unit = split[-1] if len(split) > 0 else ''
            datapoint[key] = [value, 0.0, unit]
        datapoint['uts'] = time.timestamp()
    return datapoints


def _process_mpr(fn: str, **kwargs) -> tuple[list, dict, dict]:
    """Processes an EC-Lab `.mpr` file."""
    datapoints = []
    meta = {}
    common = {}
    mpr = parse_mpr(fn)
    for module in mpr:
        name = module['header']['short_name']
        if name == b'VMP Set   ':
            meta['settings'] = module['data'].copy()
            del meta['settings']['params']
            common['params'] = module['data']['params']
        elif name == b'VMP data  ':
            datapoints = module['data']['datapoints']
        elif name == b'VMP LOG   ':
            meta['log'] = module['data']
            acquisition_start = module['data']['ole_timestamp']
            datapoints = _process_datapoints(datapoints, acquisition_start)
        elif name == b'VMP loop  ':
            meta['loops'] = module['data']
    # TODO: The right params common should be associated with the data
    # points. This can be done through the length of params and the Ns
    # column.
    return datapoints, meta, common


def _process_mpt(fn: str, **kwargs) -> tuple[list, dict, dict]:
    """Processes an EC-Lab `.mpt` file."""
    datapoints = []
    meta = {}
    common = {}
    mpt = parse_mpt(fn)
    acquisition_start = datetime.datetime.strftime(
        datetime.datetime.now(), r'%m/%d/%Y %H:%M:%S')
    if 'settings' in mpt['header']:
        meta['settings'] = mpt['header'].copy()
        del meta['settings']['params']
        common['params'] = mpt['header']['params'].copy()
        acquisition_start_match = re.search(
            r'Acquisition started on : (?P<val>.+)',
            '\n'.join(mpt['header']['settings']))
        acquisition_start = acquisition_start_match['val']
        logging.debug("Start of acquisition: %s", acquisition_start)
    if 'loops' in mpt['header']:
        meta['loops'] = mpt['header']['loops']
    # TODO: The right params common should be associated with the data
    # points. This can be done through the length of params and the Ns
    # column.
    datapoints = _process_datapoints(mpt['datapoints'], acquisition_start)
    return datapoints, meta, common


def process(fn: str, **kwargs) -> tuple[list, dict, dict]:
    """Processes an EC-Lab electrochemistry data file."""
    __, ext = os.path.splitext(fn)
    if ext == '.mpr':
        timesteps, meta, common = _process_mpr(fn, **kwargs)
    elif ext == '.mpt':
        timesteps, meta, common = _process_mpt(fn, **kwargs)
    return timesteps, meta, common
