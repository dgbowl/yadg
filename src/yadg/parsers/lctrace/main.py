import json
from scipy.signal import find_peaks, savgol_filter
import numpy as np
import logging
import uncertainties as uc

from yadg.parsers.lctrace import agilentch, agilentdx
from yadg.parsers.gctrace import (
    _parse_detector_spec,
    _find_peak_edges,
    _find_peak_maxima,
    _integrate_peaks,
    _get_smooth_yvals,
)
import yadg.dgutils

version = "4.0.dev1"


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    tracetype: str = "ch",
    detectors: dict = None,
    species: dict = None,
    calfile: str = None,
) -> tuple[list, dict, dict]:
    """
    Liquid chromatogram parser.

    This parser processes GC chromatograms in signal(time) format. When provided
    with a calibration file, this tool will integrate the trace, and provide the
    peak areas, retention times, and concentrations of the detected species.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    tracetype
        Determines the output file format. Currently supported formats are `"it"` (Agilent
        OpenLab Instrument Trace), `"ch"` (Agilent OpenLab Signal Trace), `"dx"` (Agilent
        OpenLab Data Package). The default is `"ch"`.

    detectors
        Detector specification. Matches and identifies a trace in the `fn` file. If
        provided, overrides data provided in `calfile`, below.

    species
        Species specification. Per-detector species can be listed here, providing an
        expected retention time range for the peak maximum. Additionally, calibration
        data can be supplied here. Overrides data provided in `calfile`, below.

    calfile
        Path to a json file containing the ``detectors`` and ``species`` spec. Either
        ``calfile`` and/or ``species`` and ``detectors`` have to be provided.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.
    """
    assert calfile is not None or (
        species is not None and detectors is not None
    ), "lctrace: Neither 'calfile' nor 'species' and 'detectors' were provided. Fit cannot proceed."
    lcspec = _parse_detector_spec(calfile, detectors, species)
    if tracetype == "ch":
        _data, _meta, _common = agilentch.process(fn, encoding, timezone)
    elif tracetype == "dx":
        _data, _meta, _common = agilentdx.process(fn, encoding, timezone)

    results = []
    for chrom in _data:
        peaks = {}
        comp = []
        for detname, spec in lcspec.items():
            for det in chrom["traces"].keys():
                if chrom["traces"][det]["id"] == spec["id"]:
                    chrom["traces"][det]["calname"] = detname
                    break
            units = {
                "x": chrom["traces"][det]["x"]["u"],
                "y": chrom["traces"][det]["y"]["u"],
                "A": "-",
            }
            xs, ys = chrom["traces"][det].pop("data")
            pd = spec.get("peakdetect", {})
            smooth = _get_smooth_yvals(ys[0], pd)
            peakmax = _find_peak_maxima(smooth, pd)
            peakspec = _find_peak_edges(smooth, peakmax, pd)
            integrated = _integrate_peaks(xs, ys, peakspec, spec["species"])
            peaks[detname] = {}
            for k, v in integrated.items():
                peaks[detname][k] = {
                    "peak": {
                        "max": int(v["max"]),
                        "llim": int(v["llim"]),
                        "rlim": int(v["rlim"]),
                    },
                    "A": {"n": v["A"].n, "s": v["A"].s, "u": units["A"]},
                    "h": {"n": v["h"].n, "s": v["h"].s, "u": units["y"]},
                }
                if spec["species"][k].get("calib", None) is not None:
                    x = yadg.dgutils.calib_handler(v["A"], spec["species"][k]["calib"])
                    x = max(uc.ufloat(0.0, x.s), x)
                    peaks[detname][k]["c"] = {
                        "n": x.n,
                        "s": x.s,
                        "u": spec["species"][k]["calib"].get("unit", "vol%"),
                        "uf": x,
                    }
                if k not in comp:
                    comp.append(k)
        xout = {}
        for s in comp:
            for d, ds in lcspec.items():
                if s in peaks[d] and "c" in peaks[d][s]:
                    v = peaks[d][s]["c"].pop("uf")
                    if ds.get("prefer", False) or s not in xout:
                        xout[s] = v
        norm = sum([xout[k] for k in xout.keys()])
        for s in xout:
            xnorm = xout[s] / norm
            xout[s] = {"n": xnorm.n, "s": xnorm.s, "u": "-"}
        result = {"uts": chrom.pop("uts"), "fn": chrom.pop("fn")}
        result["raw"] = chrom
        result["derived"] = {"peaks": peaks, "xout": xout}
        assert result["fn"] == fn
        results.append(result)

    return results, _meta, _common
