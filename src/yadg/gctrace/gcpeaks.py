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

#from helpers import *
from dbutils import dbstruct

_VERSION = 0.1

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

def findPeaks(xseries, yseries):
    fig = plt.figure(figsize=(5,3), dpi=128)
    ax = [fig.add_subplot(1,1,1)]
    x = range(len(yseries))
    smooth = savgol_filter(yseries, window_length=7, polyorder=3)
    smgrad = np.gradient(smooth)
    smhess = np.gradient(smgrad)
    #peaks, _ = find_peaks(smooth, prominence=np.mean(yseries)**2/max(yseries))
    ax[0].plot(x, yseries)
    #ax[0].plot(x, smooth)
    #ax[0].plot(x, smgrad)
    peaks, _ = find_peaks(yseries, prominence=1e-4*max(yseries))
    gradmax, _ = find_peaks(smgrad, prominence=1e-4*max(smgrad))
    gradmin, _ = find_peaks(-smgrad, prominence=1e-4*max(smgrad))
    #ax[0].plot(x,[i/max(smgrad) for i in smgrad])
    #ax[0].plot(x,[i/max(smhess) for i in smhess])
    #xs = range(len(smooth))
    peakdata = []
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
    # r of a peak cannot be higher than l of next peak
    #if len(peakdata) >= 2:
    #    for pi in range(len(peakdata)-1):
    #        if peakdata[pi+1]["l"] - peakdata[pi]["r"] <= 1:
    #            if abs(yseries[peakdata[pi]["r"]]) < abs(yseries[peakdata[pi+1]["l"]]):
    #                peakdata[pi+1]["l"] = peakdata[pi]["r"]
    #            else:
    #                peakdata[pi]["r"] = peakdata[pi+1]["l"]
    # initial baseline pass
    for pi in range(len(peakdata)):
        if pi == 0:
            peakdata[pi]["bl"] = peakdata[pi]["l"]
            peakdata[::-1][pi]["br"] = peakdata[::-1][pi]["r"]
        else:
            if peakdata[pi-1]["r"] == peakdata[pi]["l"]:
                peakdata[pi]["bl"] = peakdata[pi-1]["bl"]
            else:
                peakdata[pi]["bl"] = peakdata[pi]["l"]
            if peakdata[::-1][pi]["r"] == peakdata[::-1][pi-1]["l"]:
                peakdata[::-1][pi]["br"] = peakdata[::-1][pi-1]["br"]
            else:
                peakdata[::-1][pi]["br"] = peakdata[::-1][pi]["r"]

        
    for peak in peakdata:
        ax[0].plot(x[peak["l"]:peak["r"]], yseries[peak["l"]:peak["r"]], color="r", linestyle=":")
        bline = np.linspace(yseries[peak["bl"]], yseries[peak["br"]], num=(peak["br"]-peak["bl"]+1))
        bl = bline[peak["l"]-peak["bl"]]
        br = bline[peak["r"]-peak["bl"]]
        ax[0].plot([x[peak["l"]],x[peak["l"]]], [bl, yseries[peak["l"]]], color="g", alpha=0.5, linestyle=":")
        ax[0].plot([x[peak["r"]],x[peak["r"]]], [br, yseries[peak["r"]]], color="r", alpha=0.5)
        ax[0].plot([x[peak["l"]],x[peak["r"]]], [bl, br], color="r")
        peak["a"] = np.trapz(np.subtract(yseries[peak["l"]:peak["r"]], bline[peak["l"]-peak["bl"]:peak["r"]-peak["bl"]]), xseries[peak["l"]:peak["r"]])
        print(f"Peak at {peak['max']} between {peak['l']} and {peak['r']}, " +
              f"with baseline between {peak['bl']} and {peak['br']} with area {peak['a']}.")
    ax[0].set_yscale("log")
    plt.tight_layout(rect=(0.0,0.0,1,1))
    plt.show()
    

def process(gcasc, **kwargs):
    results = dbstruct.newDataGram()
    results["metadata"]["version"]  = {"gcpeaks": _VERSION}
    results["metadata"]["instrument"] = gcasc["metadata"]["instrument"]
    results["metadata"]["provenance"] = {"id": gcasc["_id"], "hash": gcasc["metadata"]["hash"]}
    numy = len(gcasc["datastream"]) - 1
    pars = kwargs.pop("pars", {})
    ver = kwargs.pop("ver", 1.0)
    debug = bool(pars.pop("debug", 0))
    hashsum = hashing.hashfile(fn)
    if debug:
        print(f" Processing GC Trace file {fn}")
    data = gcasc.process(fn)
    for detector in data["detector"]:
        xseries = [i[0] for i in detector["signal"]]
        yseries = [i[1] for i in detector["signal"]]
        peaks = findPeaks(xseries, yseries)
        
