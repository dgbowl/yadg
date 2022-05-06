import json
import logging
from pydantic import BaseModel
from . import (
    ezchromasc,
    agilentcsv,
    agilentch,
    agilentdx,
    fusionjson,
    fusionzip,
)
from . import integration

logger = logging.getLogger(__name__)


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
              unit:     !!str     # optional unit for the concentration, by default %

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
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
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

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.dataschema_4_1.parameters.ChromTrace`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. All currently
        supported file formats return full date.
    """
    if parameters.filetype == "ezchrom.asc":
        _data, _meta = ezchromasc.process(fn, encoding, timezone)
    elif parameters.filetype == "agilent.csv":
        _data, _meta = agilentcsv.process(fn, encoding, timezone)
    elif parameters.filetype == "agilent.dx":
        _data, _meta = agilentdx.process(fn, encoding, timezone)
    elif parameters.filetype == "agilent.ch":
        _data, _meta = agilentch.process(fn, encoding, timezone)
    elif parameters.filetype == "fusion.json":
        _data, _meta = fusionjson.process(fn, encoding, timezone)
    elif parameters.filetype == "fusion.zip":
        _data, _meta = fusionzip.process(fn, encoding, timezone)

    if parameters.calfile is None and (
        parameters.species is None or parameters.detectors is None
    ):
        logger.warning(
            "Neither 'calfile' nor both of 'species' and 'detectors' were "
            "provided. Will proceed without peak integration."
        )
        chromspec = False
    else:
        chromspec = parse_detector_spec(
            parameters.calfile, parameters.detectors, parameters.species
        )

    results = []
    for chrom in _data:
        result = {}
        # process derived data
        if chromspec:
            result["derived"] = integration.integrate_trace(chrom["traces"], chromspec)
        else:
            for k, v in chrom["traces"].items():
                v.pop("data")
        # process raw data here
        result["uts"] = chrom.pop("uts")
        result["fn"] = chrom.pop("fn")
        result["raw"] = chrom

        results.append(result)

    return results, _meta, True
