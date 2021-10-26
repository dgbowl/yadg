import datetime
import logging
import os
import re
from typing import Union

from dgutils.dateutils import ole_to_datetime
from uncertainties import UFloat, ufloat

from eclabfiles.mpr import parse_mpr
from eclabfiles.mps import parse_mps
from eclabfiles.mpt import parse_mpt


def _process_datapoints(
    datapoints: list[dict],
    acquisition_start: Union[float, str]
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
        # Parse timestamp with regex
        start = datetime.datetime.strptime(
            acquisition_start, '%m/%d/%Y %H:%M:%S')
        pass
    elif isinstance(acquisition_start, float):
        # OLE timestamp from `.mpr` files.
        start = ole_to_datetime(acquisition_start)
    else:
        raise TypeError(f"Unknown start time type: {type(acquisition_start)}")
    # Calculate and add UTS timestamp for every datapoint
    # TODO: Units and uncertainties
    # Every value has to be in the format
    for datapoint in datapoints:
        offset = datetime.timedelta(seconds=datapoint['time/s'])
        time = start + offset
        for key, value in datapoint.items():
            split = key.split('/')
            del split[0]
            unit = split[-1] if len(split) > 0 else ''
            datapoint[key] = [value, 0.0, unit]
        datapoint['uts'] = time.timestamp()
    return datapoints


def _process_mpr(
    fn: Union[str, list[dict]],
    encoding: str = 'windows-1252',
    **kwargs: dict
) -> tuple[list, dict, dict]:
    """Processes an `.mpr` file.

    Parameters
    ----------

    Returns
    -------

    """
    datapoints = []
    meta = {}
    common = {}
    if isinstance(fn, str):
        mpr = parse_mpr(fn)
    elif isinstance(fn, list[dict]):
        mpr = fn
    else:
        raise TypeError(f"Unrecognized type: {type(fn)}")
    for module in mpr:
        name = module['header']['short_name']
        if name == b'VMP Set   ':
            meta['settings'] = module['data'].copy()
            del meta['settings']['params']
            print
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


def _process_mpt(
    fn: Union[str, dict],
    encoding: str = 'windows-1252',
    **kwargs: dict
) -> tuple[list, dict, dict]:
    """Processes an `.mpt` file.

    Parameters
    ----------

    Returns
    -------

    """
    datapoints = []
    meta = {}
    common = {}
    if isinstance(fn, str):
        mpt = parse_mpt(fn, encoding)
    elif isinstance(fn, list[dict]):
        mpt = fn
    else:
        raise TypeError(f"Unrecognized type: {type(fn)}")
    acquisition_start = datetime.datetime.strftime(
        datetime.datetime.now(), '%m/%d/%Y %H:%M:%S')
    if 'settings' in mpt['header']:
        meta['settings'] = mpt['header'].copy()
        del meta['settings']['params']
        common['params'] = mpt['header']['params'].copy()
        logging.debug(f"{mpt['header']['settings']}")
        # logging.debug(f"{mpt['header']}") TODO??
        acquisition_start_match = re.search(
            r'Acquisition started on : (?P<val>.+)',
            '\n'.join(mpt['header']['settings']))
        acquisition_start = acquisition_start_match['val']
        logging.debug(f"Start of acquisition: {acquisition_start}")
    if 'loops' in mpt['header']:
        meta['loops'] = mpt['header']['loops']
    # TODO: The right params common should be associated with the data
    # points. This can be done through the length of params and the Ns
    # column.
    datapoints = _process_datapoints(mpt['datapoints'], acquisition_start)
    return datapoints, meta, common


def _process_mps(
    fn: str,
    encoding: str = 'windows-1252',
    **kwargs: dict
) -> tuple[list, dict, dict]:
    """Processes an `.mps` file. TODO

    Parameters
    ----------

    Returns
    -------

    """
    datapoints = []
    meta = {}
    common = {}
    mps = parse_mps(fn, encoding, load_data=True)
    # TODO: How to handle data from mps files? They are not single lists
    # of datapoints but multiple datapoints sets with different metadata
    # and different common?
    for technique in mps['techniques']:
        if 'data' not in technique:
            continue
        if 'mpr' in technique['data']:
            mpr_datapoints, mpr_meta, mpr_common = _process_mpr(
                technique['data']['mpr'])
            datapoints += mpr_datapoints
        elif 'mpt' in technique['data']:
            mpt_datapoints, mpt_meta, mpt_common = _process_mpt(
                technique['data']['mpt'])
            datapoints += mpt_datapoints


def process(
    fn: str,
    encoding: str = 'windows-1252',
    **kwargs: dict
) -> tuple[list, None, None]:
    """A dummy parser.

    This parser simply returns the current time, the filename provided, and any
    `kwargs` passed.

    Parameters
    ----------
    fn
        Filename to process
    encoding
        Encoding of ``fn``, by default 'windows-1252'.

    """
    __, ext = os.path.splitext(fn)
    if ext == '.mpr':
        timesteps, meta, common = _process_mpr(fn, encoding, **kwargs)
    elif ext == '.mpt':
        timesteps, meta, common = _process_mpt(fn, encoding, **kwargs)
    elif ext == '.mps':
        # timesteps, meta, common = _process_mps(fn, encoding, **kwargs)
        raise NotImplemented("Processing of .mps files is not yet implemented")

    return timesteps, meta, common
