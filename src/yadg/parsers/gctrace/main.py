import sys
import os
import json
import math
from scipy.signal import find_peaks, savgol_filter
import numpy as np
import logging
from uncertainties import ufloat
from typing import Union

from parsers.gctrace import datasc, chromtab, fusion
from dgutils import calib_handler


def _find_peak_maxima(ys: list[ufloat], peakdetect: dict) -> dict:
    """
    Wrapper around scipy.signal.find_peaks and scipy.signal.savgol_filter.
    Returns the peak maxima, minima, and zero-points of the smoothened
    gradient and Hessian.
    """
    yseries = [i.n for i in ys]
    # find positive and negative peak indices
    peaks = {}
    res, _ = find_peaks(yseries, prominence=peakdetect.get("prominence", 1e-4*max(yseries)))
    peaks["+"] = res
    res, _ = find_peaks(yseries, prominence=peakdetect.get("prominence", 1e-4*max(yseries)))
    peaks["-"] = res
    # smoothen the chromatogram based on supplied parameters
    smooth = savgol_filter(yseries,
                           window_length=peakdetect.get("window", 7),
                           polyorder=peakdetect.get("polyorder", 3))
    # gradient: find peaks and inflection points
    grad = np.gradient(smooth)
    res = np.where(np.diff(np.sign(grad)) != 0)[0] + 1
    peaks["gradzero"] = res
    # hessian: find peaks
    hess = np.gradient(grad)
    res = np.where(np.diff(np.sign(hess)) != 0)[0] + 1
    peaks["hesszero"] = res
    return peaks

def _find_peak_edges(ys: list[ufloat], peakdata: dict, detector: dict) -> dict:
    """
    A function that, given the y-values of a trace in `ys` and the maxima,
    inflection points etc. in `peakdata`, and the peak integration `"threshold"`
    in `detector`, finds the edges `"llim"` and `"rlim"` of each peak.
    """
    threshold = detector.get("threshold", 1.0)
    allpeaks = []
    for pi in range(len(peakdata["+"])):
        pmax = peakdata["+"][pi]
        for i in range(len(peakdata["hesszero"])):
            if peakdata["hesszero"][i] > pmax:
                hi = i
                break
        for i in range(len(peakdata["gradzero"])):
            if peakdata["gradzero"][i] > pmax:
                gi = i
                break
        # right of peak: 
        rlim = False
        # peak goes at least to the first inflection point, defined by hi.
        # If there's a minimum between the first and second inflection point, 
        # that's the end of our peak:
        for i in peakdata["gradzero"][gi:]:
            if i > peakdata["hesszero"][hi] and i < peakdata["hesszero"][hi+1]:
                rlim = i
            elif i > peakdata["hesszero"][hi+1]:
                break
        # If there's not a minimum, we keep looking at inflection points until
        # the difference in their height is below threshold:
        if not rlim:
            ppt = [peakdata["hesszero"][hi], ys[peakdata["hesszero"][hi]]]
            for i in peakdata["hesszero"][hi+1:]:
                pt = [i, ys[i]]
                dp = [ppt[0] - pt[0], ppt[1] - pt[1]]
                if abs(dp[1]/dp[0]) < threshold:
                    rlim = i
                    break
                ppt = pt
        # left of peak:
        llim = False
        for i in peakdata["gradzero"][:gi][::-1]:
            if i > peakdata["hesszero"][hi-2] and i < peakdata["hesszero"][hi-1]:
                llim = i
            elif i < peakdata["hesszero"][hi-1]:
                break
        if not llim:
            ppt = [peakdata["hesszero"][hi-1], ys[peakdata["hesszero"][hi-1]]]
            for i in peakdata["hesszero"][:hi-1][::-1]:
                pt = [i, ys[i]]
                dp = [ppt[0] - pt[0], ppt[1] - pt[1]]
                if abs(dp[1]/dp[0]) < threshold:
                    llim = i
                    break
                ppt = pt
        assert rlim and llim, \
            logging.error("gctrace: Peak end finding failed.")
        allpeaks.append({"llim": llim, "rlim": rlim, "max": pmax})
    return allpeaks

def _baseline_correct(xs: list[ufloat], ys: list[ufloat], peakdata: dict) -> dict:
    """
    Function that corrects the trace defined by [`xs`, `ys`], using a baseline
    created from the linear interpolation between the `"llim"` and `"rlim"` of
    each `peak` in `peakdata`. Returns the corrected baseline.
    """
    interpolants = []
    for p in peakdata:
        if len(interpolants) == 0:
            interpolants.append([p["llim"], p["rlim"]])
        else:
            if interpolants[-1][1] == p["llim"]:
                interpolants[-1][1] = p["rlim"]
            else:
                interpolants.append([p["llim"], p["rlim"]])
    baseline = {"x": xs, "y": [y.n for y in ys]}
    for pair in interpolants:
        npoints = pair[1] - pair[0]
        interp = list(np.interp(range(npoints), 
                                [0, npoints], 
                                [baseline["y"][pair[0]], baseline["y"][pair[1]]]))
        baseline["y"] = baseline["y"][:pair[0]] + interp + baseline["y"][pair[1]:]
    corrected = {
        "x": xs,
        "y": [ys[i] - baseline["y"][i] for i in range(len(ys))],
    }
    return corrected

def _integrate_peaks(xs: list[ufloat], ys: list[ufloat], peakdata: dict, specdata: dict) -> dict:
    """
    A function which, given a trace in [`xs`, `ys`], `peakdata` containing the
    boundaries `"llim"` and `"rlim"` for each `peak`, and `specdata` containing
    the peak-maximum matching limits `"l"` and `"r"`, first assigns peaks into
    `truepeaks`, then baseline-corrects [`xs`, `ys`], and finally integrates
    the peaks using numpy.trapz().
    """
    truepeaks = {}
    for name, species in specdata.items():
        for p in peakdata:
            if xs[p["max"]] > species["l"] and xs[p["max"]] < species["r"]:
                truepeaks[name] = p
                break
    trace = _baseline_correct(xs, ys, peakdata)
    for k, v in truepeaks.items():
        A = np.trapz([i for i in trace["y"][v["llim"]:v["rlim"]+1]], [i for i in trace["x"][v["llim"]:v["rlim"]+1]])
        truepeaks[k]["A"] = A
        truepeaks[k]["h"] = trace["y"][v["max"]]
    return truepeaks
   
def _parse_detector_spec(calfile: Union[str, None], detectors: dict, species: dict) -> dict:
    """
    Combines the GC spec from the json file specified in `calfile` with the dict
    definitions provided in `detectors` and `species`.
    """
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if detectors != {}:
        for name, det in detectors.items():
            try:
                calib[name].update(det)
            except KeyError:
                calib[name] = det
    if species != {}:
        for name, sp in species.items():
            assert name in calib, \
                logging.error(f"gctrace: Detector with name {name} specified in "
                              "supplied 'species' but previously undefined.")
            try:
                calib[name]["species"].update(sp)
            except KeyError:
                calib[name]["species"] = sp
    return calib

def process(fn: str, tracetype: str = "datasc", **kwargs: dict) -> tuple[list, dict, dict]:
    """
    GC chromatogram parser.

    This parser processes GC chromatograms in signal(time) format. When provided
    with a calibration file, this tool will integrate the trace, and provide the
    peak areas, retention times, and concentrations of the detected species.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.
    
    detectors
        Detector specification. Matches and identifies a trace in the `fn` file.
        If provided, overrides data provided in `calfile`, below.
    
    species
        Species specification. Per-detector species can be listed here, providing
        an expected retention time range for the peak maximum. Additionally,
        calibration data can be supplied here. Overrides data provided in
        `calfile`, below.

    calfile
        Path to a json file containing the `detectors` and `species` spec. Either
        `calfile` and/or `species` and `detectors` have to be provided.
    
    tracetype
        Determines the output file format. Currently supported formats are 
        `"chromtab"` (), `"datasc"` (EZ-Chrom ASCII export), `"fusion"` (Fusion 
        json file). The default is `"datasc"`.

    Returns
    -------
    tuple[list, dict, dict]
        A tuple containing the results list and the metadata and common dicts.
    """
    assert "calfile" in kwargs or ("species" in kwargs and "detectors" in kwargs), \
        logging.error("gctrace: Neither 'calfile' nor 'species' and 'detectors' "
                      "were provided. Fit cannot proceed.")
    gcspec = _parse_detector_spec(calfile = kwargs.get("calfile", None), 
                                  detectors = kwargs.get("detectors", {}),
                                  species = kwargs.get("species", {}))
    if tracetype == "datasc" or tracetype == "gctrace":
        _data, _meta, _common = datasc.process(fn, **kwargs)
    elif tracetype == "chromtab":
        _data, _meta, _common = chromtab.process(fn, **kwargs)
    elif tracetype == "fusion":
        _data, _meta, _common = fusion.process(fn, **kwargs)
    results = []
    for chrom in _data:
        peaks = {}
        comp = []
        for detname, spec in gcspec.items():
            for det in chrom["detectors"].keys():
                if chrom["detectors"][det]["id"] == spec["id"]:
                    chrom["detectors"][det]["calname"] = detname
            units = {
                "x": chrom["traces"][spec["id"]]["x"][0][2],
                "y": chrom["traces"][spec["id"]]["y"][0][2]
            }
            units["A"] = f'{units["y"]} ' if units["y"] != "-" else '' + units["x"]
            xseries = [ufloat(*i) for i in chrom["traces"][spec["id"]]["x"]]
            yseries = [ufloat(*i) for i in chrom["traces"][spec["id"]]["y"]]
            peakmax = _find_peak_maxima(yseries, spec.get("peakdetect", {}))
            peakspec = _find_peak_edges(yseries, peakmax, spec.get("peakdetect", {}))
            integrated = _integrate_peaks(xseries, yseries, peakspec, spec["species"])
            peaks[detname] = {}
            for k, v in integrated.items():
                peaks[detname][k] = {
                    "peak": { "max": v["max"], "llim": v["llim"], "rlim": v["rlim"]},
                    "A": [v["A"].n, v["A"].s, units["A"]],
                    "h": [v["h"].n, v["h"].s, units["y"]]
                }
                if spec["species"][k].get("calib", None) is not None:
                    x = calib_handler(v["A"], spec["species"][k]["calib"])
                    peaks[detname][k]["c"] = [
                        max(0.0, x.n), x.s,
                        spec["species"][k]["calib"].get("unit", "vol%")
                    ]
                if k not in comp:
                    comp.append(k)
        xout = {}
        for s in comp:
            for d, ds in gcspec.items():
                if s in peaks[d] and "c" in peaks[d][s] and (ds.get("prefer", False) or s not in xout):
                    xout[s] = peaks[d][s]["c"]
        norm = sum([ufloat(*v) for k, v in xout.items()])
        for s in xout:
            xnorm = ufloat(*xout[s]) / norm
            xout[s] = [xnorm.n, xnorm.s, "-"]
        chrom["peaks"] =  peaks
        chrom["xout"] = xout
        chrom["fn"] = fn
        results.append(chrom)
    return results, _meta, _common
