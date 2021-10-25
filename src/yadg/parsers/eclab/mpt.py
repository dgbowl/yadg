#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read BioLogic's EC-Lab ASCII data files into dicts.

TODO Adjust all docstrings

Author:         Nicolas Vetsch (veni@empa.ch / nicolas.vetsch@gmx.ch)
Organisation:   EMPA Dübendorf, Materials for Energy Conversion (501)
Date:           2021-10-11

"""
import logging
import re
from io import StringIO

import pandas as pd

from .techniques import (construct_geis_params, construct_mb_params,
                         construct_peis_params, technique_params)


def _parse_technique_params(technique: str, settings: list[str]) -> dict:
    """Finds the appropriate set of technique parameters.

    Additionally takes care of the techniques that have a changing
    number of parameters.

    Parameters
    ----------
    technique
        The name of the technique.
    settings
        The lines containing all the settings including the technique
        parameters.

    Returns
    -------
    dict
        A list of parameter keys corresponding to the given technique.

    """
    params_keys = []
    if technique in technique_params.keys():
        # The easy case.
        params_keys = technique_params[technique]
    # The more complicated case.
    elif technique == 'Potentio Electrochemical Impedance Spectroscopy':
        params_keys = construct_peis_params(settings)
    elif technique == 'Galvano Electrochemical Impedance Spectroscopy':
        params_keys = construct_geis_params(settings)
    elif technique == 'Modulo Bat':
        params_keys = construct_mb_params(settings)
    else:
        raise NotImplementedError(f"Technique '{technique}' not implemented.")
    params = settings[-len(params_keys):]
    # The sequence param columns are always allocated 20 characters.
    n_sequences = int(len(params[0])/20)
    params_values = []
    for seq in range(1, n_sequences):
        params_values.append([param[seq*20:(seq+1)*20].strip()
                             for param in params])
    # TODO: Translate the parameters from str to the appropriate type.
    params = [dict(zip(params_keys, values)) for values in params_values]
    return params, len(params_keys)


def _parse_loop_indexes(loops_lines: list[str]) -> dict:
    """Parses the loops section of an MPT file header.

    The function puts together the loop indexes like they are saved in
    MPR files.

    Parameters
    ----------
    loops_lines
        The MPT file loops section as a list of strings.

    Returns
    -------
    dict
        A dictionary with the number of loops and the loop indexes.

    """
    n_loops = int(
        re.match(r'Number of loops : (?P<val>.+)', loops_lines[0])['val'])
    loop_indexes = []
    for loop in range(n_loops):
        index = re.match(
            r'Loop (.+) from point number (?P<val>.+) to (.+)',
            loops_lines[loop+1])['val']
        loop_indexes.append(int(index))
    return {'n': n_loops, 'indexes': loop_indexes}


def _parse_header(lines: list[str], n_header_lines: int) -> dict:
    """Parses the header part of an MPT file including loops.

    Parameters
    ----------
    lines
        All the lines of the MPT file (except the two very first ones).
    n_header_lines
        The number of header lines from the line after the MPT file
        magic.

    Returns
    -------
    dict
        A dictionary containing the technique name, the general
        settings, and a list of technique parameters.

    """
    header = {}
    if n_header_lines == 3:
        logging.info("No settings present in given MPT file.")
        header['technique'] = lines[0].strip()
        return header
    # At this point the first two lines have already been read.
    header_lines = lines[:n_header_lines-3]
    header_sections = ''.join(header_lines).split(sep='\n\n')
    technique_name = header_sections[0].strip()
    settings_lines = header_sections[1].split('\n')
    header['technique'] = technique_name
    header['params'], n_params = _parse_technique_params(
        technique_name, settings_lines)
    header['settings'] = [line.strip() for line in settings_lines[:n_params]]
    if len(header_sections) == 3:
        # The header contains a loops section.
        loops_lines = header_sections[2].split('\n')
        header['loops'] = _parse_loop_indexes(loops_lines)
    return header


def _parse_datapoints(lines: list[str], n_header_lines: int) -> list[dict]:
    """Parses the data part of an MPT file.

    Parameters
    ----------
    lines
        All the lines of the MPT file as a list.
    n_header_lines
        The number of header lines parsed from the top of the MPT file.

    Returns
    -------
    list[dict]
        A list of dicts, each corresponding to a single data point.

    """
    # At this point the first two lines have already been read.
    data_lines = lines[n_header_lines-3:]
    data = pd.read_csv(
        StringIO(''.join(data_lines)),
        sep='\t',
        encoding='windows-1252')
    # Remove the extra column due to an extra tab in MPT files.
    data = data.iloc[:, :-1]
    return data.to_dict(orient='list')


def parse_mpt(path: str, encoding: str = 'windows-1252') -> dict:
    """Parses an EC-Lab MPT file.

    Parameters
    ----------
    path
        Filepath of the EC-Lab MPT file to read in.

    Returns
    -------
    dict
        A dict containing all the parsed MPT data.

    """
    file_magic = 'EC-Lab ASCII FILE\n'
    with open(path, 'r', encoding=encoding) as mpt:
        if mpt.readline() != file_magic:
            raise ValueError("Invalid file magic for given MPT file.")
        logging.info("Reading `.mpt` file...")
        n_header_lines = int(mpt.readline().strip().split()[-1])
        lines = mpt.readlines()
        logging.info("Parsing `.mpt` header...")
        header = _parse_header(lines, n_header_lines)
        logging.info("Parsing `.mpt` data...")
        datapoints = _parse_datapoints(lines, n_header_lines)
    return {'header': header, 'data': datapoints}
