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

from helpers import *
from . import gcasc

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
    #fig = plt.figure(figsize=(5,3), dpi=128)
    #ax = [fig.add_subplot(1,1,1)]
    #x = range(len(yseries))
    #ax[0].plot(x, yseries)
    # 1) let's smoothen the chromatogram based on supplied or good default parameters
    smooth = savgol_filter(yseries, window_length=detector.get("window", 7),
                                    polyorder=detector.get("poly", 3))
    smgrad = np.gradient(smooth)
    smhess = np.gradient(smgrad)
    # 2) find peaks and inflection points
    peaks, _ = find_peaks(yseries, prominence=detector.get("prominence", 1e-4*max(yseries)))
    gradmax, _ = find_peaks(smgrad, prominence=0.1*detector.get("prominence", 1e-3*max(smgrad)))
    gradmin, _ = find_peaks(-smgrad, prominence=0.1*detector.get("prominence", 1e-3*max(smgrad)))
    peakdata = []
    # 2) assign left and right limits of peaks based on their maxima and first derivatives
    for i in peaks:
        for ii in gradmax[::-1]:
            if ii < i:
                break
        for jj in gradmin:
            if jj > i:
                break
        leftgrad = math.sqrt(smgrad[ii])*1e-3
        iii = ii
        while smgrad[iii] > leftgrad and iii > 0:
            iii -= 1
        rightgrad = math.sqrt(-smgrad[jj])*1e-4
        jjj = jj
        while smgrad[jjj] < -rightgrad and jjj < len(smgrad)-1:
            jjj += 1
        peakdata.append({"max": i, "l": iii+1, "r": jjj})
    # 3) initial guess for baseline limits
    for pi in range(len(peakdata)):
        if pi == 0:
            peakdata[pi]["bl"] = peakdata[pi]["l"]
            peakdata[::-1][pi]["br"] = peakdata[::-1][pi]["r"]
        else:
            if peakdata[pi-1]["r"] + 2 >= peakdata[pi]["l"]:
                peakdata[pi]["bl"] = peakdata[pi-1]["bl"]
                peakdata[pi-1]["r"] = peakdata[pi]["l"] + 1
            else:
                peakdata[pi]["bl"] = peakdata[pi]["l"]
            if peakdata[::-1][pi]["r"] + 2 >= peakdata[::-1][pi-1]["l"]:
                peakdata[::-1][pi]["br"] = peakdata[::-1][pi-1]["br"]
                peakdata[::-1][pi]["r"] = peakdata[::-1][pi-1]["l"] + 1
            else:
                peakdata[::-1][pi]["br"] = peakdata[::-1][pi]["r"]
    mult = detector["species"].get("units", "s")
    if mult == "min":
        mult = 60
    else:
        mult = 1
    results = {}
    for peak in peakdata:
        #ax[0].plot(x[peak["l"]:peak["r"]], yseries[peak["l"]:peak["r"]], color="r", linestyle=":")
        bline = np.linspace(yseries[peak["bl"]], yseries[peak["br"]], num=(peak["br"]-peak["bl"]+1))
        bl = bline[peak["l"]-peak["bl"]]
        br = bline[peak["r"]-peak["bl"]]
        #ax[0].plot([x[peak["l"]],x[peak["l"]]], [bl, yseries[peak["l"]]], color="g", alpha=0.5, linestyle=":")
        #ax[0].plot([x[peak["r"]-1],x[peak["r"]-1]], [br, yseries[peak["r"]-1]], color="r", alpha=0.5)
        #ax[0].plot([x[peak["l"]],x[peak["r"]]], [bl, br], color="r")
        peak["a"] = np.trapz(np.subtract(yseries[peak["l"]:peak["r"]], bline[peak["l"]-peak["bl"]:peak["r"]-peak["bl"]]), xseries[peak["l"]:peak["r"]])
        for ident in detector["species"]:
            if ident != "units" and \
               detector["species"][ident]["l"]*mult <= xseries[peak["max"]] and \
               detector["species"][ident]["r"]*mult >= xseries[peak["max"]]:
                results[ident] = {"A": peak["a"], "h": yseries[peak["max"]], "rt": xseries[peak["max"]]}
                if "rf" in detector["species"][ident]:
                    results[ident]["X"] = max(0, peak["a"] / detector["species"][ident]["rf"])
    return results
                
                #ax[0].fill_between(x[peak["l"]:peak["r"]], yseries[peak["l"]:peak["r"]], bline[peak["l"]-peak["bl"]:peak["r"]-peak["bl"]])
    #plt.tight_layout(rect=(0.0,0.0,1,1))
    #plt.show()
    
    
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
    results = gcasc.process(fn, **kwargs)
    for det in detectors:
        if detectors[det]["id"] in results["trace"]:
            xseries = results["trace"]["t"]
            yseries = results["trace"][detectors[det]["id"]]
            peaks = _findPeaks(xseries, yseries, detectors[det])
            results[det] = peaks
    results["fn"] = fn
    keep = kwargs.get("store", [])
    for k in ["trace", "units"]:
        if k not in keep:
            results.pop(k)
    return results
            
