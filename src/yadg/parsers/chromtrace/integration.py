"""
.. _parsers_chromtrace_integration:

This module contains the :func:`yadg.parsers.chromtrace.integration.integrate_trace`
function, as well as several helper functions to smoothen, peak-pick, determine edges,
and integrate the supplied traces.

Smoothing
`````````
Smoothing can be optionally performed on the Y-values of each trace, using a 
Savigny-Golay filter. The default smoothing is performed using a cubic fit to a window 
length of 7; if the polyorder or the window length are not specified, smoothing is 
not used.

Peak-picking and edge-finding
`````````````````````````````
Peak-picking is performed on the smoothed Y-data to find peaks, as well as on the mirror
image of the data to find bands. Only peaks are further processed. Additionally, the
1st and 2nd derivatives of the Y-data are evaluated, and the zero-points are found using
numpy routines.

The peak edges are taken as either the nearest minima adjacent to the peak maximum,
or as the inflection points at which the gradient falls below a prescribed threshold,
whichever is closest to the peak maximum.

Baseline correction
```````````````````
Using the determined peak-edges, the baseline is linearly interpolated in sections of
Y-data which belong to a peak. The interpolation is performed using the raw (not 
smoothened) Y-data. 

If multiple peaks are adjacent to each other without a gap, the interpolation begins
at the left limit of the leftmost peak and continues uninterrupted to the right limit
of the rightmost peak. The points which belong to the interpolated areas are assumed 
to have an uncertainty of zero.

The corrected baseline is then obtained by subtracting the interpolated baseline from
the original raw (not smoothened) data.

Peak integration
````````````````
Peak integration is performed on the corrected baseline and the matching X-data using
the trapezoidal method as implemented in ``np.trapz``.

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""
import numpy as np
from scipy.signal import savgol_filter, find_peaks
import logging
import uncertainties as uc
from uncertainties import unumpy as unp

import yadg.dgutils


def _get_smooth_yvals(yvals: np.ndarray, pd: dict) -> np.ndarray:
    """
    Wrapper around :func:`scipy.signal.savgol_filter`. If the window length and the
    polynomial order are specified in ``pd``, the smoothened ``yvals`` are returned.
    Otherwise, the original ``yvals`` are returned.

    The function also validates that the specified window length derived from the
    ``"window"`` is larger than the ``"polyorder"``.
    """
    if pd.get("polyorder", None) is None or pd.get("window", None) is None:
        logging.info("chromtrace: no smoothing.")
        return yvals
    else:
        window = pd.get("window", 3) * 2 + 1
        polyorder = pd.get("polyorder", 3)
        assert polyorder < window, f"chromtrace: specified window <= polyorder."
        if polyorder == 2:
            logging.warning(
                "chromtrace: smoothing with a polyorder == 2 can be unreliable. "
                "Consider switching to a higher polyorder or disabling smoothing "
                "completely."
            )
        return savgol_filter(yvals, window_length=window, polyorder=polyorder)


def _find_peak_maxima(yvals: np.ndarray, pd: dict) -> dict:
    """
    This function is a wrapper around :func:`scipy.signal.find_peaks` as well as
    a helper finding the points at which the gradient and Hessian of ``yvals``
    is zero (maxima, minima, inflection points).
    """
    # find positive and negative peak indices
    peaks = {}
    res, _ = find_peaks(yvals, prominence=pd.get("prominence", 1e-4 * yvals.max()))
    peaks["+"] = res
    res, _ = find_peaks(yvals * -1, prominence=pd.get("prominence", 1e-4 * yvals.max()))
    peaks["-"] = res
    # gradient: find peaks and inflection points
    grad = np.gradient(yvals)
    res = np.nonzero(np.diff(np.sign(grad)))[0] + 1
    peaks["gradzero"] = res
    # second derivative: find peaks
    hess = np.gradient(grad)
    res = np.nonzero(np.diff(np.sign(hess)))[0] + 1
    peaks["hesszero"] = res
    return peaks, grad, hess


def _find_peak_edges(
    yvals: np.ndarray, ygrad: np.ndarray, peakdata: dict, detector: dict
) -> dict:
    """
    A function that, given the y-values of a trace in ``yvals`` and the maxima,
    inflection points etc. in ``peakdata``, and the peak integration `"threshold"`
    in ``detector``, finds the edges ``"llim"`` and ``"rlim"`` of each peak.
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
        rmin = False
        rthr = False
        for xi in range(peakdata["hesszero"][hi], yvals.size):
            if xi in peakdata["gradzero"] and not rmin:
                rmin = xi
            if xi in peakdata["hesszero"][hi:] and not rthr:
                if abs(ygrad[xi]) < threshold:
                    rthr = xi
            if rthr and rmin:
                break
        rlim = min(rthr if rthr else yvals.size, rmin if rmin else yvals.size)
        if rlim == yvals.size:
            logging.warning("gctrace: possible mismatch of peak end.")
            rlim -= 1
        # left of peak
        lmin = False
        lthr = False
        for xi in range(0, peakdata["hesszero"][hi - 1])[::-1]:
            if xi in peakdata["gradzero"] and not lmin:
                lmin = xi
            if xi in peakdata["hesszero"][: hi - 1] and not lthr:
                if abs(ygrad[xi]) < threshold:
                    lthr = xi
            if lthr and lmin:
                break
        llim = max(lthr if lthr else 0, lmin if lmin else 0)
        if llim == 0:
            logging.warning("gctrace: possible mismatch of peak start.")
        allpeaks.append({"llim": llim, "rlim": rlim, "max": pmax})
    return allpeaks


def _get_baseline(ys: list[np.ndarray], peakdata: dict) -> list[np.ndarray]:
    """
    Function that returns a baseline based on the trace defined by ``ys``. The
    baseline is created by a linear interpolation between the ``"llim"`` and
    ``"rlim"`` of each `peak` in ``peakdata``. Returns the corrected baseline.
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
    bn = ys[0].copy()
    bs = ys[1].copy()
    for pair in interpolants:
        n = pair[1] - pair[0]
        interp = np.interp(range(n), [0, n], [bn[pair[0]], bn[pair[1]]])
        bn[pair[0] : pair[1]] = interp
        bs[pair[0] : pair[1]] = np.zeros(n)
    return bn, bs


def _integrate_peaks(
    xs: list[np.ndarray],
    ys: list[np.ndarray],
    peakdata: dict,
    specdata: dict,
) -> dict:
    """
    A function which, given a trace in [`xs`, `ys`], `peakdata` containing the boundaries
    `"llim"` and `"rlim"` for each `peak`, and `specdata` containing the peak-maximum
    matching limits `"l"` and `"r"`, first assigns peaks into `truepeaks`, then
    baseline-corrects [`xs`, `ys`], and finally integrates the peaks using numpy.trapz().
    """
    xsn = xs[0]
    truepeaks = {}
    for name, species in specdata.items():
        for p in peakdata:
            if xsn[p["max"]] > species["l"] and xsn[p["max"]] < species["r"]:
                truepeaks[name] = p
                break
    bln = _get_baseline(ys, peakdata)
    for k, v in truepeaks.items():
        s = v["llim"]
        e = v["rlim"] + 1
        py = unp.uarray(ys[0][s:e] - bln[0][s:e], ys[1][s:e] - bln[1][s:e])
        px = unp.uarray(xs[0][s:e], xs[1][s:e])
        A = np.trapz(py, px)
        truepeaks[k]["A"] = A
        truepeaks[k]["h"] = py[v["max"] - s]
    return truepeaks


def integrate_trace(traces: dict, chromspec: dict) -> tuple[dict, dict]:
    """
    Integration, calibration, and normalisation handling function. Used to process
    all chromatographic data for which a calibration has been provided

    Parameters
    ----------
    traces
        A dictionary of trace data, with keys being the "raw" name of the detector,
        and the values containing the ``"id"`` for specification matching, and a
        ``"data"`` tuple containing the ``(xs, ys)`` where each element is a pair of
        :class:`(np.ndarray)` with the nominal values and standard deviations.

    chromspec
        Parsed calibration information, with keys being the detector names in the
        calibration file, and values containing the ``"id"`` for detector matching,
        ``"peakdetect"`` dictionary with peak-picking and edge-finding settings,
        and ``"species"`` dictionary with names of species as keys and the left,
        right limits and calibration information as values.

    Returns
    -------
    (peaks, xout): tuple[dict, dict]
        A tuple containing a dictionary with the peak picking information (name,
        maximum, limits, height, area) as well as a dictionary containing the
        normalised molar fractions of the assigned and detected species.
    """

    peaks = {}
    comp = []
    for detname, spec in chromspec.items():
        for det in traces.keys():
            if traces[det]["id"] == spec["id"]:
                traces[det]["calname"] = detname
                break
        units = {
            "t": traces[det]["t"]["u"],
            "y": traces[det]["y"]["u"],
            "A": "-",
        }
        xs, ys = traces[det].pop("data")
        pd = spec.get("peakdetect", {})
        smooth = _get_smooth_yvals(ys[0], pd)
        peakmax, ygrad, _ = _find_peak_maxima(smooth, pd)
        peakspec = _find_peak_edges(smooth, ygrad, peakmax, pd)
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
        for d, ds in chromspec.items():
            if s in peaks[d] and "c" in peaks[d][s]:
                v = peaks[d][s]["c"].pop("uf")
                if ds.get("prefer", False) or s not in xout:
                    xout[s] = v
    norm = sum([xout[k] for k in xout.keys()])
    for s in xout:
        xnorm = xout[s] / norm
        xout[s] = {"n": xnorm.n, "s": xnorm.s, "u": "-"}
    return peaks, xout
