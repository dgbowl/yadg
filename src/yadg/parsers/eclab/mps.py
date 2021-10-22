#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read BioLogic's EC-Lab settings files into dicts.

Author:         Nicolas Vetsch (veni@empa.ch / nicolas.vetsch@gmx.ch)
Organisation:   EMPA Dübendorf, Materials for Energy Conversion (501)
Date:           2021-10-13

"""
import glob
import logging
import os

from .mpr import parse_mpr
from .mpt import parse_mpt
from .techniques import (construct_geis_params, construct_mb_params,
                         construct_peis_params, technique_params)


def _parse_header(headers: list[str]) -> dict:
    """Parses the header of an MPS file."""
    header = {}
    header['filename'] = headers[0].strip().split()[-1]
    header['general_settings'] = [line.strip()
                                  for line in headers[1].split('\n')]
    return header


def _parse_techniques(technique_sections: list[str]) -> list:
    """Parses the techniques section of an MPS file."""
    techniques = []
    for section in technique_sections:
        technique = {}
        technique_lines = section.split('\n')
        technique_name = technique_lines[1]
        technique['technique'] = technique_name
        params = technique_lines[2:]
        params_keys = []
        if technique_name in technique_params.keys():
            # The easy case.
            params_keys = technique_params[technique_name]
        # The more complicated case.
        elif technique_name == 'Potentio Electrochemical Impedance Spectroscopy':
            params_keys = construct_peis_params(params)
        elif technique_name == 'Galvano Electrochemical Impedance Spectroscopy':
            params_keys = construct_geis_params(params)
        elif technique_name == 'Modulo Bat':
            params_keys = construct_mb_params(params)
        else:
            raise NotImplementedError(
                f"Technique '{technique_name}' not implemented.")
        # The sequence param columns are always allocated 20 characters.
        n_sequences = int(len(params[0])/20)
        params_values = []
        for seq in range(1, n_sequences):
            params_values.append(
                [param[seq*20:(seq+1)*20].strip() for param in params])
        # TODO: Translate the parameters from str to the appropriate type.
        params = [dict(zip(params_keys, values)) for values in params_values]
        technique['params'] = params
        techniques.append(technique)
    return techniques


def _load_technique_data(
    techniques: list[dict],
    mpr_paths: list[str],
    mpt_paths: list[str]
) -> list[dict]:
    """Tries to load technique data from the same folder.

    TODO: This can probably be done in a more idiomatic way than what is
    done here.

    Parameters
    ----------
    techniques
        The previously parsed list of technique dicts.
    mpr_paths
        A list of paths to MPR files to read in.
    mpt_paths
        A list of paths to MPT files to read in.

    Returns
    -------
    list[dict]
        The list of technique dictionaries now including any data.

    """
    # Determine the number of files that are expected and initialize the
    # data sections. Loops and wait do not write data.
    n_expected_files = 0
    for technique in techniques:
        if technique['technique'] in {'Wait', 'Loop'}:
            continue
        n_expected_files += 1
        technique['data'] = {}
    # Parse any MPR files.
    if n_expected_files == len(mpr_paths):
        # Sorting is assumed to put the files in the right order.
        mpr_paths = sorted(mpr_paths)
        i = 0
        for technique in techniques:
            if technique['technique'] in {'Wait', 'Loop'}:
                continue
            technique['data']['mpr'] = parse_mpr(mpr_paths[i])
            i += 1
    # Parse any MPT files.
    if n_expected_files == len(mpt_paths):
        # Sorting is assumed to put the files in the right order.
        mpt_paths = sorted(mpt_paths)
        i = 0
        for technique in techniques:
            if technique['technique'] in {'Wait', 'Loop'}:
                continue
            technique['data']['mpt'] = parse_mpt(mpt_paths[i])
            i += 1
    return techniques


def parse_mps(path: str, load_data: bool = True) -> dict:
    """Parses an EC-Lab MPS file.

    If there are MPR or MPT files present in the same folder, those
    files are read in and returned as well. MPT files are preferred, as
    they contain slightly more info.

    Parameters
    ----------
    path
        Filepath of the EC-Lab MPS file to read in.
    parse_data
        Whether to parse the associated data

    Returns
    -------
    dict
        A dict containing all the parsed MPS data and MPT/MPR data in
        case it exists.

    """
    file_magic = 'EC-LAB SETTING FILE\n'
    with open(path, 'r', encoding='windows-1252') as mps:
        if mps.readline() != file_magic:
            raise ValueError("Invalid file magic for given MPS file.")
        logging.info("Reading `.mps` file...")
        sections = mps.read().split('\n\n')
        n_linked_techniques = int(sections[0].strip().split()[-1])
        logging.info("Parsing `.mps` header...")
        header = _parse_header(sections[1:3])
        logging.info("Parsing `.mps` techniques...")
        techniques = _parse_techniques(sections[3:])
    if len(techniques) != n_linked_techniques:
        raise ValueError(
            "The number of parsed techniques does not match the number "
            "of linked techniques in the header.")
    base_path, __ = os.path.splitext(path)
    mpr_paths = glob.glob(base_path + '*.mpr')
    mpt_paths = glob.glob(base_path + '*.mpt')
    if (load_data and (mpr_paths or mpt_paths)):
        logging.info("Loading technique data from `.mpt`/`.mpr`...")
        techniques = _load_technique_data(techniques, mpr_paths, mpt_paths)
    return {'header': header, 'techniques': techniques}
