import os
import logging
from scipy.signal import find_peaks
import numpy as np

import uncertainties as uc
from uncertainties import unumpy as unp


import yadg.dgutils
from yadg.parsers.qftrace import fit, prune, labviewcsv

version = "4.0.0"


def _fit(
    fvals: np.ndarray,
    fsigs: np.ndarray,
    gvals: np.ndarray,
    absgvals: np.ndarray,
    method: str,
    height: float,
    distance: float,
    cutoff: float,
    threshold: float,
) -> tuple[dict]:
    """
    Function that fits Q and f from Γ(f).
    """
    Qs = {"n": [], "s": [], "u": "-"}
    fs = {"n": [], "s": [], "u": "Hz"}
    mag = -10 * np.log10(absgvals)
    peaks, _ = find_peaks(mag, height=height, distance=distance)
    assert len(peaks) > 0, logging.error("qftrace: No peaks were found.")
    npeaks = len(peaks)
    if method == "lorentz":
        _prune = prune.gradient
        _fitq = fit.lorentz
        _ppar = threshold
    elif method == "kajfez" or method == "q0refl":
        _prune = prune.cutoff
        _fitq = fit.kajfez
        _ppar = cutoff
    elif method == "naive":
        _prune = prune.gradient
        _fitq = fit.naive
        _ppar = threshold
    for p in peaks:
        # prune using a smaller number of points
        n = gvals.size
        os = max(0, p - max(1000, n // 5))
        oe = min(n, p + max(1000, n // 5))
        s, e = _prune(p - os, absgvals[os:oe], _ppar)
        s = os + s
        e = os + e
        Q, f = _fitq(fvals[s:e], fsigs[s:e], gvals[s:e], absgvals[s:e])
        Qs["n"].append(Q.n)
        Qs["s"].append(Q.s)
        fs["n"].append(f.n)
        fs["s"].append(f.s)
    assert len(Qs["n"]) == npeaks and len(fs["n"]) == npeaks
    return Qs, fs


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "timezone",
    tracetype: str = "labview.csv",
    method: str = "kajfez",
    height: float = 1.0,
    distance: float = 5000.0,
    cutoff: float = 0.4,
    threshold: float = 1e-6,
) -> tuple[list, dict, dict]:
    """
    VNA reflection trace parser.

    This parser processes a VNA log file, containing the complex reflection coefficient
    data as a function of frequency (:math:`\\Gamma(f)`). This data is automatically
    worked up to produce the quality factor :math:`Q_0` and the central frequency
    :math:`f_0` of all peaks found in each trace; hence the name ``qftrace``.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    method
        Method used for fitting :math:`Q_0` and :math:`f_0` to :math:`\\Gamma(f)` data.
        One of ``"naive"``, ``"lorentz"``, or ``"kajfez"``. Default is ``"kajfez"``.

    cutoff
        Parameter passed to the cutoff-based pruning routine, defining the cutoff
        threshold for the normalisation. Default is 0.4.

    threshold
        Parameter passed to the gradient-based pruning routine, defining the minimum
        gradient below which the trace gets pruned. Default is 1e-6.

    height
        Parameter for the peak-picker.

    distance
        Parameter for the peak-picker.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.
    """
    if tracetype == "labview.csv":
        data, meta = labviewcsv.process(fn, encoding, timezone)
    for ts in data:
        for det, trace in ts["raw"]["traces"].items():
            Q, f = _fit(
                trace.pop("fvals"),
                trace.pop("fsigs"),
                trace.pop("gamma"),
                trace.pop("absgamma"),
                method,
                height,
                distance,
                cutoff,
                threshold,
            )
            if "derived" not in ts:
                ts["derived"] = {}
            ts["derived"][det] = {"Q": Q, "f": f}
    return data, meta, None
