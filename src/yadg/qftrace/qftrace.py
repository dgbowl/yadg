import os
import datetime
from scipy.signal import find_peaks
import math

from . import q0refl
from . import lorentz
from . import naive
from ..helpers import *



def _fit(freq, comp, method, **kwargs):
    cutoff = kwargs.get("cutoff", 0.4)
    height = kwargs.get("height", 1.0)
    absl = [abs(i) for i in comp]
    results = {
              "fit": { 
                  "method": method,
                  "cutoff": cutoff,
                  "height": height
              },
              "acquisition": {    
                  "points": len(freq),
                  "start": freq[0],
                  "stop": freq[-1]
              },   
              "Q0": [],
              "f0": [],
              "pruned": [],
              "imag": [i.imag for i in comp],
              "real": [i.real for i in comp],
              "gamma": absl,
              "freq": freq
              }
    mag = [-10*math.log(i,10) for i in absl]
    peaks, properties = find_peaks(mag, height=height, distance=5000)
    if len(peaks) == 0:
        peaks = [mag.index(max(mag))]
    results["npeaks"] = len(peaks)
    if method == "lorentz":
        _prune = lorentz.prune
        _fitq = lorentz.fit
    elif method == "q0refl":
        _prune = q0refl.prune
        _fitq = q0refl.fit
    elif method == "naive":
        _prune = naive.prune
        _fitq = naive.fit
    for p in peaks:
        px, py = _prune(p, freq, comp, absl, **kwargs)
        results["pruned"].append(len(px))
        Q0, f0 = _fitq(px, py, **kwargs)
        results["Q0"].append(Q0)
        results["f0"].append(f0)
    return results

def process(fn, **kwargs):
    dirname, basename = os.path.split(fn)
    results = {
              "uts": dateutils.coerceDashedDate(basename[:-4]),
              "path": fn
              }
    with open(fn, "r") as infile:
        lines = infile.readlines()
        if len(lines) < 2:
            return None
        freq = []
        comp = []
        if len(lines[0].strip().split(";")) > 1:
            h = 1
            for pair in lines[0].strip().split(";"):
                k, v = [each.strip() for each in pair.split("=")]
                kwargs[k.lower()] = float(v)
        else:
            h = 0
        for line in lines[h:]:
            f, r, i = line.strip().split()
            freq.append(float(f))
            comp.append(complex(float(r), float(i)))
        if float(r) == 0.0 and float(i) == 0.0:
            return None
        results.update(_fit(freq, comp, method = kwargs.pop("method", "lorentz"), **kwargs))
        if kwargs.get("debug", False):
            for peak in range(results["npeaks"]):
                print(f'qftrace: peak index {peak:1d}, Q0 = {results["Q0"][peak]:7.2f}, f0 = {results["f0"][peak]:10.0f}')
        keep = kwargs.get("store", ["Q0", "f0", "pruned"])
        for k in ["Q0", "f0", "pruned", "imag", "real", "gamma", "freq"]:
            if k not in keep:
                results.pop(k)
        results["acquisition"].update({"bandwith": kwargs.pop("bw", 500),
                                       "avg": kwargs.pop("avg", 10)})
    return results
