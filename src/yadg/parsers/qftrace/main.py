import os
import logging
from scipy.signal import find_peaks
from uncertainties import ufloat, unumpy
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
) -> tuple[int, list, list]:
    """
    Function that fits Q and f from Γ(f).
    """
    Qs = []
    fs = []
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
        Qs.append([Q.n, Q.s, "-"])
        fs.append([f.n, f.s, "Hz"])
    assert len(Qs) == npeaks and len(fs) == npeaks
    return Qs, fs


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "timezone",
    atol: float = 0.0,
    rtol: float = 5e-7,
    sigma: dict = {},
    method: str = "kajfez",
    height: float = 1.0,
    distance: float = 5000.0,
    cutoff: float = 0.4,
    threshold: float = 1e-6,
    **kwargs,
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

    atol
        Default absolute uncertainty in f and Re(Γ) / Im(Γ). By default set to 0.0

    rtol
        Default relative uncertainty in f and Re(Γ) / Im(Γ). By default set to 5e-7, as significant digits are printed in the standard output.

    sigma
        Property-specific `atol` and `rtol` can be supplied here.

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
    if ";" in lines[0]:
        items = lines.pop(0).split(";")
        for item in items:
            if item.startswith("BW"):
                common["bandwith"] = [float(item.split("=")[-1].strip()), 0.5, "Hz"]
            if item.startswith("AVG"):
                common["averaging"] = int(item.split("=")[-1].strip())
    # calculate precision of trace
    _tols = {"atol": atol, "rtol": rtol}
    data["raw"] = {"f": [], "Re(Γ)": [], "Im(Γ)": [], "abs(Γ)": []}
    freq = []
    gamma = []
    absgamma = []
    for line in lines:
        f, r, i = line.strip().split()
        f = float(f)
        ftol = max(
            sigma.get("f", _tols)["atol"], abs(f * sigma.get("f", _tols)["rtol"])
        )
        freq.append(ufloat(f, ftol))
        data["raw"]["f"].append([f, ftol, "Hz"])
        c = complex(float(r), float(i))
        gamma.append(c)
        ctol = max(
            sigma.get("Γ", _tols)["atol"], abs(c * sigma.get("Γ", _tols)["rtol"])
        )
        data["raw"]["Re(Γ)"].append([float(r), ctol, "-"])
        data["raw"]["Im(Γ)"].append([float(i), ctol, "-"])
        absgamma.append(ufloat(abs(c), abs(complex(ctol, ctol))))
        data["raw"]["abs(Γ)"].append([abs(c), abs(complex(ctol, ctol)), "-"])
    common["height"] = height
    common["distance"] = distance
    common["method"] = method
    if method == "kajfez":
        common["cutoff"] = cutoff
    else:
        common["threshold"] = threshold
    Q, f = _fit(
        np.asarray(freq),
        np.asarray(gamma),
        np.asarray(absgamma),
        method,
        height,
        distance,
        cutoff,
        threshold,
    )
    data["derived"] = {"Q": Q, "f": f, "npeaks": len(Q)}
    return [data], None, common
