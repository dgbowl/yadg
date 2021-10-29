import os
import logging
from scipy.signal import find_peaks
from uncertainties import ufloat, ufloat_fromstr, unumpy, umath
import numpy as np

import yadg.dgutils
from yadg.parsers.qftrace import kajfez, lorentz, naive, prune

version = "1.0.dev1"


def _fit(
    freq: np.ndarray,
    gamma: np.ndarray,
    absgamma: np.ndarray,
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
    mag = -10 * unumpy.log10(absgamma)
    peaks, _ = find_peaks([i.n for i in mag], height=height, distance=distance)
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
        pf, pg, pag = _prune(p, freq, gamma, absgamma, _ppar)
        Q, f = _fitq(pf, pg, pag)
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
    threshold: float = 1e-6
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
    bw = ufloat(10000,1)
    avg = 15
    if ";" in lines[0]:
        items = lines.pop(0).split(";")
        for item in items:
            if item.startswith("BW"):
                bw = ufloat_fromstr(item.split("=")[-1].strip())
                common["bandwith"] = {"n": bw.n, "s": bw.s, "u": "Hz"}
            if item.startswith("AVG"):
                avg = int(item.split("=")[-1].strip())
                common["averaging"] = avg
    # calculate precision of trace
    data["raw"] = {
        "f": {"n": [], "s": [], "u": "Hz"}, 
        "Re(Γ)": {"n": [], "s": [], "u": "-"},
        "Im(Γ)": {"n": [], "s": [], "u": "-"}, 
        "abs(Γ)": {"n": [], "s": [], "u": "-"}
    }
    freq = []
    gamma = []
    real = []
    imag = []
    absgamma = []
    for line in lines:
        f, re, im = line.strip().split()
        f = ufloat_fromstr(f)
        f.std_dev = max(f.s, bw/avg)
        re = ufloat_fromstr(re)
        im = ufloat_fromstr(im)
        freq.append(f)
        real.append(re)
        imag.append(im)
        gamma.append(complex(re.n, im.n))
        absgamma.append(umath.sqrt(re*re + im*im))
    freq = np.asarray(freq)
    gamma = np.asarray(gamma)
    real = np.asarray(real)
    imag = np.asarray(imag)
    absgamma = np.asarray(absgamma)

    data["raw"]["f"]["n"] = unumpy.nominal_values(freq).tolist()
    data["raw"]["f"]["s"] = unumpy.std_devs(freq).tolist()
    data["raw"]["Re(Γ)"]["n"] = unumpy.nominal_values(real).tolist()
    data["raw"]["Re(Γ)"]["s"] = unumpy.std_devs(real).tolist()
    data["raw"]["Im(Γ)"]["n"] = unumpy.nominal_values(imag).tolist()
    data["raw"]["Im(Γ)"]["s"] = unumpy.std_devs(imag).tolist()
    data["raw"]["abs(Γ)"]["n"] = unumpy.nominal_values(absgamma).tolist()
    data["raw"]["abs(Γ)"]["s"] = unumpy.std_devs(absgamma).tolist()
    common["height"] = height
    common["distance"] = distance
    common["method"] = method
    if method == "kajfez":
        common["cutoff"] = cutoff
    else:
        common["threshold"] = threshold
    Q, f = _fit(
        freq,
        gamma,
        absgamma,
        method,
        height,
        distance,
        cutoff,
        threshold,
    )
    data["derived"] = {"Q": Q, "f": f}
    return [data], None, common
