import json
import numpy as np
import logging
import uncertainties as uc
import uncertainties.unumpy as unp

from yadg.parsers.chromtrace import (
    ezchromasc,
    agilentcsv,
    agilentch,
    agilentdx,
    fusionjson,
)
from yadg.parsers.chromtrace import integration

version = "4.0.0"


def parse_detector_spec(
    calfile: str = None, detectors: dict = None, species: dict = None
) -> dict:
    """
    Chromatography detector parser.

    Combines the specification provided in ``calfile`` with that provided in
    ``detectors`` and ``species``.

    .. _parsers_chromtrace_calfile:

    The format of ``calfile`` is as follows:

    .. code-block:: yaml

        "{{ detector_name }}":    # name of the detector
          id:           !!int     # ID of the detector used for matching
          prefer:       !!bool    # whether to prefer this detector for xout calc
          peakdetect:
            window:     !!int     # Savigny-Golay window_length = 2*window + 1
            polyorder:  !!int     # Savigny-Golay polyorder
            prominence: !!float   # peak picking prominence parameter
            threshold:  !!float   # peak edge detection threshold
          species:
            "{{ species_name }}": # name of the analyte
              l:        !!float   # peak picking left limit [s]
              r:        !!float   # peak picking right limit [s]
              calib:    {}        # calibration specification

    .. note::
        The syntax of the calibration specification is detailed in
        :func:`yadg.dgutils.calib.calib_handler`.

    .. _parsers_chromtrace_detectors:

    The format of ``detectors`` is as follows:

    .. code-block:: yaml

        "{{ detector_name }}":  # name of the detector
          id:           !!int   # ID of the detector used for matching
          prefer:       !!bool  # whether to prefer this detector for xout calc
          peakdetect:
            window:     !!int   # Savigny-Golay window_length = 2*window + 1
            polyorder:  !!int   # Savigny-Golay polyorder
            prominence: !!float # peak picking prominence parameter
            threshold:  !!float # peak edge detection threshold

    .. _parsers_chromtrace_species:

    The format of ``species`` is as follows:

    .. code-block:: yaml

        "{{ detector_name }}":    # name of the detector
          species:
            "{{ species_name }}": # name of the analyte
              l:        !!float   # peak picking left limit [s]
              r:        !!float   # peak picking right limit [s]
              calib:    !!calib   # calibration specification

    .. note::
        The syntax of the calibration specification is detailed in
        :func:`yadg.dgutils.calib.calib_handler`.

    Parameters
    ----------
    calfile
        A json file containing the calibration data in the format prescribed
        :ref:`above<parsers_chromtrace_calfile>`.

    detectors
        A dictionary containing the ``"id"``, ``"peakdetect"`` and ``"prefer"``
        keys for each detector, as shown :ref:`here<parsers_chromtrace_detectors>`.

    species
        A dictionary containing the species names as keys and their specification
        as dictionaries, as shown :ref:`here<parsers_chromtrace_species>`.

    Returns
    -------
    calib: dict
        The combined calibration specification.
    """

    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if isinstance(detectors, dict):
        for name, det in detectors.items():
            try:
                calib[name].update(det)
            except KeyError:
                calib[name] = det
    if isinstance(species, dict):
        for name, sp in species.items():
            assert name in calib, (
                f"chromtrace: Detector with name {name} specified in supplied "
                f"'species' but previously undefined."
            )
            try:
                calib[name]["species"].update(sp)
            except KeyError:
                calib[name]["species"] = sp
    return calib


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    tracetype: str = "ezchrom.asc",
    detectors: dict = None,
    species: dict = None,
    calfile: str = None,
) -> tuple[list, dict, dict]:
    """
    Unified chromatogram parser.

    This parser processes GC and LC chromatograms in signal(time) format. When
    provided with a calibration file, this tool will integrate the trace, and provide
    the peak areas, retention times, and concentrations of the detected species.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    tracetype
        Determines the output file format. Currently supported formats are:

        -  ``"ezchrom.asc"`` (EZ-Chrom ASCII export),
        -  ``"agilent.csv"`` (Agilent Chemstation chromtab csv format),
        -  ``"agilent.ch"`` (Agilent OpenLab binary signal file),
        -  ``"agilent.dx"`` (Agilent OpenLab binary data archive),
        -  ``"fusion.json"`` (Fusion json file),

        The default is ``"ezchrom.asc"``.

    detectors
        Detector specification. Matches and identifies a trace in the `fn` file.
        If provided, overrides data provided in ``calfile``, below.

    species
        Species specification. Per-detector species can be listed here, providing an
        expected retention time range for the peak maximum. Additionally, calibration
        data can be supplied here. Overrides data provided in ``calfile``, below.

    calfile
        Path to a json file containing the ``detectors`` and ``species`` spec. Either
        ``calfile`` and/or ``species`` and ``detectors`` have to be provided.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.
    """
    if tracetype == "ezchrom.asc":
        _data, _meta = ezchromasc.process(fn, encoding, timezone)
    elif tracetype == "agilent.csv":
        _data, _meta = agilentcsv.process(fn, encoding, timezone)
    elif tracetype == "agilent.dx":
        _data, _meta = agilentdx.process(fn, encoding, timezone)
    elif tracetype == "agilent.ch":
        _data, _meta = agilentch.process(fn, encoding, timezone)
    elif tracetype == "fusion.json":
        _data, _meta = fusionjson.process(fn, encoding, timezone)

    if calfile is None and (species is None or detectors is None):
        logging.warning(
            "chromtrace: Neither 'calfile' nor both 'species' and 'detectors' were "
            "provided. Will proceed without peak integration."
        )
        chromspec = False
    else:
        chromspec = parse_detector_spec(calfile, detectors, species)

    results = []
    for chrom in _data:
        result = {}
        # process derived data
        if chromspec:
            peaks, xout = integration.integrate_trace(chrom["traces"], chromspec)
            result["derived"] = {"peaks": peaks, "xout": xout}
        else:
            for k, v in chrom["traces"].items():
                v.pop("data")
        # process raw data here
        result["uts"] = chrom.pop("uts")
        result["fn"] = chrom.pop("fn")
        result["raw"] = chrom

        results.append(result)

    return results, _meta, None
