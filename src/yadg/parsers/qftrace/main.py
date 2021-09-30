import os
import logging
from scipy.signal import find_peaks
from uncertainties import ufloat, umath
from uncertainties import unumpy as unp
import numpy as np

import dgutils
from parsers.qftrace import kajfez, lorentz, naive, prune

def _fit(freq, gamma, absgamma, method, height, distance, cutoff, threshold):
    """
    Function that fits Q and f from Γ(f).
    """
    results = {
        "Q": [],
        "f": []
    }
    mag = [-10*unp.log(ufloat(*i),10) for i in absgamma]
    peaks, _ = find_peaks([i.n for i in mag], height = height, distance = distance)
    if len(peaks) == 0:
        peaks = [np.argmax(mag)]
    results["npeaks"] = len(peaks)
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
        pf, pg, pag = _prune(p, [ufloat(*i) for i in freq], [i[0] for i in gamma], 
                            [ufloat(*i) for i in absgamma], _ppar)
        Q, f = _fitq(pf, pg, pag)
        results["Q"].append([Q.n, Q.s, "-"])
        results["f"].append([f.n, f.s, "Hz"])
    return results

def process(fn, atol = 0, rtol = 5e-7, sigma = {}, method = "kajfez", 
            height = 1.0, distance = 5000, cutoff = 0.4, threshold = 1e-6, **kwargs):
    """
    VNA reflection trace parser.

    This parser processes a VNA log file, containing the reflection data as a
    function of frequency. This data is automatically worked up to produce the
    quality factor Q and the central frequency f of all peaks found in the trace;
    hence the name qftrace. 

    Parameters
    ----------
    fn : string
        File to process

    atol : float, optional
        Default absolute uncertainty in f and Re(Γ) / Im(Γ). By default set to 0.

    rtol : float, optional
        Default relative uncertainty in f and Re(Γ) / Im(Γ). By default set to
        5e-7, as 7 significant digits are printed in the standard output.
    
    sigma : dict, optional
        Property-specific `atol` and `rtol` can be supplied here.
    
    method : string, optional
        Method for fitting Q and f to Γ(f) data. One of "naive", "lorentz", or 
        "kajfez". Default is "kajfez".
    
    cutoff : float, optional
        Parameter passed to the cutoff-based pruning routine, defining the 
        cutoff threshold for the normalisation. Default is 0.4.
    
    threshold: float, optional
        Parameter passed to the gradient-based pruning routine, defining the
        minimum gradient below which the trace gets pruned. Default is 1e-6.

    height : float, optional
        Parameter for the peak-picker, 

    distance : float, optional
        Parameter for the peak-picker, 

    """
    # create timestamp
    _, datefunc = dgutils.infer_timestamp_from([], 
                            spec = {"timestamp": [0, "%Y-%m-%d-%H-%M-%S"]})
    dirname, basename = os.path.split(fn)
    data = {
            "uts": datefunc(os.path.splitext(basename)[0]),
            "fn": fn
    }
    common = {}
    with open(fn, "r") as infile:
        lines = infile.readlines()
    assert len(lines) > 2, \
        logging.error(f"qftrace: Only {len(lines)-1} points supplied in "
                      f"{fn}; fitting impossible." )
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
    data["trace"] = {
        "f": [],
        "Γ": [],
        "abs(Γ)": []
    }
    for line in lines:
        f, r, i = line.strip().split()
        f = float(f)
        ftol = max(sigma.get("f", _tols)["atol"], abs(f*sigma.get("f", _tols)["rtol"]))
        data["trace"]["f"].append([f, ftol, "Hz"])
        c = complex(float(r), float(i))
        ctol = max(sigma.get("f", _tols)["atol"], abs(c*sigma.get("f", _tols)["rtol"]))
        data["trace"]["Γ"].append([c, complex(ctol, ctol), "-"])
        data["trace"]["abs(Γ)"].append([abs(c), abs(complex(ctol,ctol)), "-"])
    common["height"] = height
    common["distance"] = distance
    common["method"] = method
    if method == "kajfez":
        common["cutoff"] = cutoff
    else:
        common["threshold"] = threshold
    data.update(_fit(data["trace"]["f"], data["trace"]["Γ"], data["trace"]["abs(Γ)"], 
                     method, height, distance, cutoff, threshold))
    return [data], None, common
