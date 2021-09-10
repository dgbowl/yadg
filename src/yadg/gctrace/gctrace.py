import sys
import os
import json
import math
import peakutils
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter
from scipy.interpolate import interp1d
import numpy as np
import copy
import matplotlib
import matplotlib.pyplot as plt

from ..helpers import *
from . import gcasc
from . import chromtab

def parseFilename(fn, folder, detpar, debug = 0):
    if debug:
        print("Processing FN: {:s}".format(fn))
    path = os.path.join(folder, fn)
    data = gcasc.process(path)
    blines = []
    for detname in detpar:
        blines.append([])
        detector = detpar[detname]
        unit = detector["species"].pop("units", "s")
        if unit in ["s", "second"]:
            pass
        elif unit in ["m", "min", "minute"]:
            for s in detector["species"]:
                minutes = detector["species"][s]
                detector["species"][s] = [i*60 for i in minutes]
        if debug:
            peakareas, bline = baseline.correct(data[detector["id"]]["x"], data[detector["id"]]["y"],
                                                [detector["species"][k] for k in detector["species"]],
                                                window = detector["window"], poly = detector["poly"],
                                                prominence = detector["prominence"],
                                                return_baseline = True)
            blines[-1].append([[i/60.0 for i in data[detector["id"]]["x"]], data[detector["id"]]["y"], bline])
        else:
            peakareas = baseline.correct(data[detector["id"]]["x"], data[detector["id"]]["y"],
                                     [detector["species"][k] for k in detector["species"]],
                                     window = detector["window"], poly = detector["poly"],
                                     prominence = detector["prominence"])
        
        data[detname] = {}
        for k in detector["species"]:
            data[detname][k] = peakareas.pop(0)
            if debug:
                print(" Peak area {0:15s}: {1: 10.2f}".format(k, data[detname][k]))
    if debug != 0:
        return(data, blines)
    else:
        return(data)

def lowpass(values, width = 10, cut=2):
    x = np.linspace(0,1,len(values))
    fval = np.fft.fft(values)
    filtered = np.array(np.fft.fft(np.minimum(values,cut)))
    filtered *= np.exp(-x**2/width) + np.exp(-(1-x)**2/width)
    temp = np.fft.ifft(filtered)
    return(temp)

def running_mean(x, width):
    return np.convolve(x, np.ones((width,))/width, mode="same")

def _findPeaks(xseries, yseries, detector):
    debug = False
    if debug:
        fig = plt.figure(figsize=(5,3), dpi=128)
        ax = [fig.add_subplot(1,1,1)]
        x = range(len(yseries))
        ax[0].plot(x, yseries)
    # 1) let's smoothen the chromatogram based on supplied or good default parameters
    smooth = savgol_filter(yseries, window_length=detector.get("window", 7),
                                    polyorder=detector.get("poly", 3))
    smgrad = np.gradient(smooth)
    smhess = np.gradient(smgrad)
    # 2) find peaks and inflection points
    peaks, _ = find_peaks(yseries, prominence=detector.get("prominence", 1e-4*max(yseries)))
    neg_peaks, _ = find_peaks([-y for y in yseries], prominence=detector.get("prominence", 1e-4*max(yseries)))
    gradmax, _ = find_peaks(smgrad, prominence=0.1*detector.get("prominence", 1e-3*max(smgrad)))
    gradmin, _ = find_peaks(-smgrad, prominence=0.1*detector.get("prominence", 1e-3*max(smgrad)))
    peakdata = []
    # 3) filter found peaks based on detector spec
    mult = detector["species"].get("units", "s")
    if mult == "min":
        mult = 60
    else:
        mult = 1
    for i in list(peaks):
        for ident in detector["species"]:
            if ident != "units" and \
              detector["species"][ident]["l"]*mult <= xseries[i] and \
              detector["species"][ident]["r"]*mult >= xseries[i] and \
              detector["species"][ident].get("rf", 1.0) > 0:    
                peakdata.append({"max": i, "sign": True, "name": ident})
    for i in list(neg_peaks):
        for ident in detector["species"]:
            if ident != "units" and \
              detector["species"][ident]["l"]*mult <= xseries[i] and \
              detector["species"][ident]["r"]*mult >= xseries[i] and \
              detector["species"][ident].get("rf", 1.0) < 0:    
                peakdata.append({"max": i, "sign": False, "name": ident})
    peakdata = sorted(peakdata, key = lambda k: k["max"])
    
    # 2) assign left and right limits of peaks based on their maxima and first derivatives
    colors = ["r","g","b","cyan","purple","orange"]
    for i in range(len(peakdata)):
        if peakdata[i]["sign"]:
            for ii in gradmax[::-1]:
                if ii < peakdata[i]["max"]:
                    break
            for jj in gradmin:
                if jj > peakdata[i]["max"]:
                    break
        else:
            for jj in gradmax:
                if jj > peakdata[i]["max"]:
                    break
            for ii in gradmin[::-1]:
                if ii < peakdata[i]["max"]:
                    break
        # peaks tend to tail - use jj as threshold gradient
        leftgrad = math.sqrt(abs(smgrad[jj]))*1e-5
        iii = ii
        while iii > 0 and abs(smgrad[iii]) > leftgrad and (smgrad[iii] > 0) == peakdata[i]["sign"]:
            iii -= 1
        rightgrad = math.sqrt(abs(smgrad[jj]))*1e-5
        jjj = jj
        while jj < len(smgrad)-1 and abs(smgrad[jjj]) > rightgrad and (smgrad[jjj] < 0) == peakdata[i]["sign"]:
            jjj += 1
        peakdata[i].update({"l": iii, "r": jjj-1})
        
    # 3) initial guess for baseline limits
    for pi in range(len(peakdata)):
        if pi == 0:
            peakdata[pi]["bl"] = peakdata[pi]["l"]
            peakdata[::-1][pi]["br"] = peakdata[::-1][pi]["r"]
        else:
            if "bl" not in peakdata[pi]:
                peakdata[pi]["bl"] = peakdata[pi]["l"]
            if peakdata[pi-1]["r"] + 2 >= peakdata[pi]["l"]:
                peakdata[pi]["bl"] = peakdata[pi-1]["bl"]
            if "br" not in peakdata[::-1][pi]:
                peakdata[::-1][pi]["br"] = peakdata[::-1][pi]["r"]
            if peakdata[::-1][pi]["r"] + 2 >= peakdata[::-1][pi-1]["l"]:
                peakdata[::-1][pi]["br"] = peakdata[::-1][pi-1]["br"]

    # 4) second baseline guess correcting for crosses with data
    for pi in range(len(peakdata)):
        if peakdata[pi]["sign"] == False:
            bline = np.linspace(smooth[peakdata[pi]["bl"]], smooth[peakdata[pi]["br"]],
                               num = (peakdata[pi]["br"]-peakdata[pi]["bl"] + 1))
            bdata = smooth[peakdata[pi]["bl"]:peakdata[pi]["br"]+1]
            bdiff = [bdata[i] - bline[i] for i in range(len(bline))]
            if peakdata[pi]["l"] == peakdata[pi]["bl"]:
                pass
            elif bdiff[peakdata[pi]["l"] - peakdata[pi]["bl"]] < 0:
                pass
            else:
                oldl = peakdata[pi]["l"]
                newl = oldl + 1
                while bdiff[newl - peakdata[pi]["bl"]] > 0:
                    newl += 1
                peakdata[pi]["l"] = newl
                if pi != 0:
                    peakdata[pi-1]["r"] = newl
            if peakdata[pi]["r"] == peakdata[pi]["br"]:
                pass
            elif bdiff[peakdata[pi]["r"] - peakdata[pi]["bl"]] < 0:
                pass
            else:
                oldr = peakdata[pi]["r"]
                newr = oldr - 1
                while bdiff[newr - peakdata[pi]["bl"]] > 0:
                    newr -= 1
                peakdata[pi]["r"] = newr
                if pi < len(peakdata) - 1:
                    peakdata[pi+1]["l"] = newr
                
    # 4) correct peak edges for overlaps
    for pi in range(1, len(peakdata)):
        if peakdata[pi-1]["r"] > peakdata[pi]["l"]:
            newl = int(round((peakdata[pi-1]["r"] + peakdata[pi]["l"])/2))
            peakdata[pi-1]["r"] = newl
            peakdata[pi]["l"] = newl
        elif peakdata[pi-1]["r"] + 2 >= peakdata[pi]["l"]:
            peakdata[pi-1]["r"] = peakdata[pi]["l"] + 1
    
        
    for i in range(len(peakdata)):
        if debug:
            ax[0].plot(peakdata[i]["max"], yseries[peakdata[i]["max"]], marker="v", color=colors[i])
            ax[0].plot(peakdata[i]["l"], yseries[peakdata[i]["l"]], marker="|", color=colors[i])
            ax[0].plot(peakdata[i]["r"], yseries[peakdata[i]["r"]], marker="|", color=colors[i])
            ax[0].plot(peakdata[i]["bl"], yseries[peakdata[i]["bl"]], marker=".", color=colors[i])
            ax[0].plot(peakdata[i]["br"], yseries[peakdata[i]["br"]], marker=".", color=colors[i])
    results = {}
    for peak in peakdata:
        if debug:
            ax[0].plot(x[peak["l"]:peak["r"]], yseries[peak["l"]:peak["r"]], color="r", linestyle=":")
        bline = np.linspace(yseries[peak["bl"]], yseries[peak["br"]], num=(peak["br"]-peak["bl"]+1))
        bl = bline[peak["l"]-peak["bl"]]
        br = bline[peak["r"]-peak["bl"]]
        if debug:
            ax[0].plot([x[peak["l"]],x[peak["l"]]], [bl, yseries[peak["l"]]], color="g", alpha=0.5, linestyle=":")
            ax[0].plot([x[peak["r"]-1],x[peak["r"]-1]], [br, yseries[peak["r"]-1]], color="r", alpha=0.5)
            ax[0].plot([x[peak["l"]],x[peak["r"]]], [bl, br], color="r")
        peak["a"] = np.trapz(np.subtract(yseries[peak["l"]:peak["r"]], bline[peak["l"]-peak["bl"]:peak["r"]-peak["bl"]]), xseries[peak["l"]:peak["r"]])
        if peak["name"] == "":
            pass
        else:
            results[peak["name"]] = {"A": peak["a"], "h": yseries[peak["max"]], "rt": xseries[peak["max"]]}
            if "rf" in detector["species"][peak["name"]]:
                results[peak["name"]]["x"] = max(0, peak["a"] / detector["species"][peak["name"]]["rf"])
            if debug:
                ax[0].fill_between(x[peak["l"]:peak["r"]], yseries[peak["l"]:peak["r"]], bline[peak["l"]-peak["bl"]:peak["r"]-peak["bl"]])
    if debug:
        plt.tight_layout(rect=(0.0,0.0,1,1))
        plt.show()
    return results
    
    
def _parseDetectorSpec(**kwargs):
    instspecs = ["detectors", "calfile"]
    assert len(set(instspecs) & set(kwargs)) == 1, \
        f'GCTRACE: you have to provide instrument data either as a "calfile" or in a "detectors" structure'
    if "calfile" in kwargs:
        with open(kwargs["calfile"], "r") as infile:
            jsdata = json.load(infile)
            assert "detectors" in jsdata, \
                f'GCTRACE: "calfile" formatted improperly: has to contain a "detectors" entry.'
            detectors = jsdata["detectors"]
    else:
        detectors = kwargs["detectors"]
    return detectors

def process(fn, **kwargs):
    detectors = _parseDetectorSpec(**kwargs)
    tracetype = kwargs.get("tracetype", "gcasc")
    if tracetype == "gcasc":
        results = gcasc.process(fn, **kwargs)
    elif tracetype == "chromtab":
        results = chromtab.process(fn, **kwargs)
    for ri in range(len(results)):
        for det in detectors:
            if detectors[det]["id"] in results[ri]["trace"]:
                xseries = results[ri]["trace"][detectors[det]["id"]]["t"]
                yseries = results[ri]["trace"][detectors[det]["id"]]["y"]
                peaks = _findPeaks(xseries, yseries, detectors[det])
                results[ri][det] = peaks
        results[ri]["fn"] = fn
        keep = kwargs.get("store", [])
        for k in ["trace"]:
            if k not in keep:
                results[ri].pop(k)
    return results
            
