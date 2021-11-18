import os
import logging
from scipy.signal import find_peaks
import numpy as np

import uncertainties as uc
from uncertainties import unumpy as unp
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

import yadg.dgutils
from yadg.parsers.qftrace import kajfez, lorentz, naive, prune

version = "1.0.dev1"


def _fit(
    freq: list[np.ndarray],
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
    fvals, fsigs = freq
    Qs = {"n": [], "s": [], "u": "-"}
    fs = {"n": [], "s": [], "u": "Hz"}
    mag = -10 * np.log10(absgvals)
    peaks, _ = find_peaks(mag, height=height, distance=distance)
    assert len(peaks) > 0, logging.error("qftrace: No peaks were found.")
    npeaks = len(peaks)
    if method == "lorentz":
        _prune = prune.gradient
        _fitq = lorentz.fit
        _ppar = threshold
    elif method == "kajfez" or method == "q0refl":
        _prune = prune.cutoff
        _fitq = kajfez.fit
        _ppar = cutoff
    elif method == "naive":
        _prune = prune.gradient
        _fitq = naive.fit
        _ppar = threshold
    for p in peaks:
        # prune using a smaller number of points
        n = gvals.size
        os = max(0, p - max(1000, n // 5))
        oe = min(n, p + max(1000, n // 5))
        s, e = _prune(p - os, fvals[os:oe], gvals[os:oe], absgvals[os:oe], _ppar)
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
    method: str = "kajfez",
    height: float = 1.0,
    distance: float = 5000.0,
    cutoff: float = 0.4,
    threshold: float = 1e-6,
) -> tuple[list, dict, dict]:
    """
    VNA reflection trace parser.

    This parser processes a VNA log file, containing the reflection data as a function of frequency. This data is automatically worked up to produce the quality factor Q and the central frequency f of all peaks found in the trace; hence the name qftrace.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    method
        Method for fitting Q and f to Γ(f) data. One of ``"naive"``, ``"lorentz"``, or ``"kajfez"``. Default is ``"kajfez"``.

    cutoff
        Parameter passed to the cutoff-based pruning routine, defining the cutoff threshold for the normalisation. Default is 0.4.

    threshold
        Parameter passed to the gradient-based pruning routine, defining the minimum gradient below which the trace gets pruned. Default is 1e-6.

    height
        Parameter for the peak-picker.

    distance
        Parameter for the peak-picker.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.
    """
    # create timestamp
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        timezone=timezone, spec={"timestamp": {"format": "%Y-%m-%d-%H-%M-%S"}}
    )
    dirname, basename = os.path.split(fn)
    data = {"uts": datefunc(os.path.splitext(basename)[0]), "fn": str(fn)}
    common = dict()
    with open(fn, "r", encoding=encoding) as infile:
        lines = infile.readlines()
    assert (
        len(lines) > 2
    ), f"qftrace: Only {len(lines)-1} points supplied in {fn}; fitting impossible."
    # process header
    bw = [10000.0, 1.0]
    avg = 15
    if ";" in lines[0]:
        items = lines.pop(0).split(";")
        for item in items:
            if item.startswith("BW"):
                bw = tuple_fromstr(item.split("=")[-1].strip())
                common["bandwith"] = {"n": bw[0], "s": bw[1], "u": "Hz"}
            if item.startswith("AVG"):
                avg = int(item.split("=")[-1].strip())
                common["averaging"] = avg
    fsbw = bw[0] / avg
    # calculate precision of trace
    data["raw"] = {
        "f": {"n": [], "s": [], "u": "Hz"},
        "Re(Γ)": {"n": [], "s": [], "u": "-"},
        "Im(Γ)": {"n": [], "s": [], "u": "-"},
    }
    freq = []
    gamma = []
    real = []
    imag = []
    absgamma = []
    for line in lines:
        f, re, im = line.strip().split()
        fn, fs = tuple_fromstr(f)
        fs = max(fs, fsbw)
        ren, res = tuple_fromstr(re)
        imn, ims = tuple_fromstr(im)
        freq.append([fn, fs])
        real.append([ren, res])
        imag.append([imn, ims])
        c = complex(ren, imn)
        gamma.append(c)
        absgamma.append(abs(c))
    freq = [np.array(i) for i in zip(*freq)]
    data["raw"]["f"]["n"], data["raw"]["f"]["s"] = [i.tolist() for i in freq]
    real = [np.array(i) for i in zip(*real)]
    data["raw"]["Re(Γ)"]["n"], data["raw"]["Re(Γ)"]["s"] = [i.tolist() for i in real]
    imag = [np.array(i) for i in zip(*imag)]
    data["raw"]["Im(Γ)"]["n"], data["raw"]["Im(Γ)"]["s"] = [i.tolist() for i in imag]
    common["height"] = height
    common["distance"] = distance
    common["method"] = method
    if method == "kajfez":
        common["cutoff"] = cutoff
    else:
        common["threshold"] = threshold
    Q, f = _fit(
        freq,
        np.array(gamma),
        np.array(absgamma),
        method,
        height,
        distance,
        cutoff,
        threshold,
    )
    data["derived"] = {"Q": Q, "f": f}
    return [data], None, common
