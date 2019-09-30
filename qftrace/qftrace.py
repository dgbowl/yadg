import os
import datetime
from . import q0refl
from scipy.signal import find_peaks
import math

import matplotlib.pyplot as plt

def _prune(p0, freq, comp, cutoff = 0.4):
    pruned = []
    mag = [abs(i) for i in comp]
    min_v = mag[p0]
    max_v = max(mag)
    pf = []
    pc = []
    for l in range(p0-1):
        li = p0 - l
        norm = (mag[li] - min_v) / (max_v - min_v)
        if norm <= cutoff:
            pf.insert(0, freq[li])
            pc.insert(0, comp[li])
        else:
            break
    for r in range(len(mag) - p0):
        ri = p0 + r
        norm = (mag[ri] - min_v) / (max_v - min_v)
        if norm <= cutoff:
            pf.append(freq[ri])
            pc.append(comp[ri])
        else:
            break
    return pf[1:-1], pc[1:-1]



def _fit(freq, comp, iterations = 5, cutoff = 0.4, height=1.0):
    results = {
              "fit": { 
                  "iterations": iterations,
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
              "gamma": [abs(i) for i in comp],
              "freq": freq
              }
    mag = [-10*math.log(abs(i),10) for i in comp]
    peaks, properties = find_peaks(mag, height=height, distance=5000)
    if len(peaks) == 0:
        peaks = [mag.index(max(mag))]
    results["npeaks"] = len(peaks)
    for p in peaks:
        pfreq, pcomp = _prune(p, freq, comp, cutoff = cutoff)
        results["pruned"].append(len(pfreq))
        Q0, f0 = q0refl.fit(pfreq, pcomp, iterations = iterations)
        results["Q0"].append(Q0)
        results["f0"].append(f0)
    return results

def process(fn, **kwargs):
    dirname, basename = os.path.split(fn)
    year, month, day, hour, minute, second = [int(i) for i in basename[:-4].split("-")]
    dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    results = {
              "uts": dt.timestamp(),
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
        results.update(_fit(freq, comp, iterations = kwargs.pop("iterations", 5), 
                                        cutoff = kwargs.pop("cutoff", 0.4),
                                        height = kwargs.pop("height", 1.0)))
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
