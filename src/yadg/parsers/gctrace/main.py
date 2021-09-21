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
import logging
from uncertainties import ufloat

from helpers import *
from parsers.gctrace import datasc, chromtab

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

def _find_peaks(xs, ys, detector):
    xseries = [i.n for i in xs]
    yseries = [i.n for i in ys]
    # find positive and negative peak indices
    peaks = {}
    res, _ = find_peaks(yseries, prominence=detector.get("prominence", 1e-4*max(yseries)))
    peaks["+"] = res
    res, _ = find_peaks(yseries, prominence=detector.get("prominence", 1e-4*max(yseries)))
    peaks["-"] = res
    # smoothen the chromatogram based on supplied parameters
    smooth = savgol_filter(yseries,
                           window_length=detector.get("window", 7),
                           polyorder=detector.get("polyorder", 3))
    # gradient: find peaks and inflection points
    grad = np.gradient(smooth)
    res, _ = find_peaks(grad, prominence=0.1*detector.get("prominence", 1e-3*max(grad)))
    peaks["gradmax"] = res
    res, _ = find_peaks(-grad, prominence=0.1*detector.get("prominence", 1e-3*max(grad)))
    peaks["gradmin"] = res
    res = np.where(np.diff(np.sign(grad)) != 0)[0] + 1
    peaks["gradzero"] = res
    # hessian: find peaks
    hess = np.gradient(grad)
    res = np.where(np.diff(np.sign(hess)) != 0)[0] + 1
    peaks["hesszero"] = res
    return peaks

def _integrate_peaks(xs, ys, peakdata, specdata):
    debug = True
    truepeaks = {}
    for name, species in specdata.items():
        assert species.get("rf", 1) > 0, \
            logging.error(f"gctrace: RF of species {name} is less than 0. "
                          "Negative peaks not yet supported.")
        for pmax in peakdata["+"]:
            if xs[pmax].n > species["l"] and xs[pmax].n < species["r"]:
                truepeaks[name] = pmax
    print(truepeaks)
    fig = plt.figure(figsize=(5,3), dpi=128)
    ax = [fig.add_subplot(1,1,1)]
    ax[0].plot([x.n for x in xs], [y.n for y in ys])
    ax[0].scatter([xs[i].n for i in peakdata["+"]], [ys[i].n for i in peakdata["+"]], color="C0")
    ax[0].scatter([xs[v].n for k, v in truepeaks.items()], [ys[v].n for k, v in truepeaks.items()], color="r", marker = "x")
    #ax[0].scatter([xs[i].n for i in peakdata["gradzero"]], [ys[i].n for i in peakdata["gradzero"]], color="k")
    ax[0].scatter([xs[i].n for i in peakdata["hesszero"]], [ys[i].n for i in peakdata["hesszero"]], color="k", marker = "x")
    
    for pname, pmax in truepeaks.items():
        pi = list(peakdata["+"]).index(pmax)
        nextpeak = peakdata["+"][pi+1]
        prevpeak = peakdata["+"][pi-1]
        for hess in peakdata["hesszero"]:
            if hess > pmax:
                nexthess = hess
                break
        hi = list(peakdata["hesszero"]).index(nexthess)
        prevhess = peakdata["hesszero"][hi-1]
        pprevhess = peakdata["hesszero"][hi-2]
        nnexthess = peakdata["hesszero"][hi+1]
        print(pname, prevpeak, pprevhess, prevhess, pmax, nexthess, nnexthess, nextpeak)
        ax[0].plot([x.n for x in xs[prevhess:nexthess]], [y.n for y in ys[prevhess:nexthess]], color="C1", linestyle=":")
    plt.show()
    assert False
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
    
    
def _parse_detector_spec(calfile, detectors, species):
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if detectors != {}:
        for name, det in detectors.items():
            try:
                calib[name].update(det)
            except KeyError:
                calib[name] = det
    if species != {}:
        for name, sp in species.items():
            assert name in calib, \
                logging.error(f"gctrace: Detector with name {name} specified in "
                              "supplied 'species' but previously undefined.")
            try:
                calib[name]["species"].update(sp)
            except KeyError:
                calib[name]["species"] = sp
    return calib

def process(fn, tracetype = "datasc", **kwargs):
    """
    GC chromatogram parser.

    This parser processes GC chromatograms in signal(time) format. When provided
    with a calibration file, this tool will integrate the trace, and provide the
    peak areas, retention times, and concentrations of the detected species.

    Parameters
    ----------

    fn : string
        The file containing the trace(s) to parse.
    
    detectors : dict, optional
        Detector specification. Matches and identifies a trace in the `fn` file.
        If provided, overrides data provided in `calfile`, below.
    
    species : dict, optional
        Species specification. Per-detector species can be listed here, providing
        an expected retention time range for the peak maximum. Additionally,
        calibration data can be supplied here. Overrides data provided in
        `calfile`, below.

    calfile : string, optional
        Path to a json file containing the `detectors` and `species` spec. Either
        `calfile` and/or `species` and `detectors` have to be provided.
    
    tracetype : string, optional
        Determines the output file format. Currently supported formats are 
        `"chromtab"` (), `"datasc"` (EZ-Chrom ASCII export), `"fusion"` (Fusion 
        json file). The default is `"datasc"`.
    """
    assert "calfile" in kwargs or ("species" in kwargs and "detectors" in kwargs), \
        logging.error("gctrace: Neither 'calfile' nor 'species' and 'detectors' "
                      "were provided. Fit cannot proceed.")
    calib = _parse_detector_spec(calfile = kwargs.get("calfile", None), 
                                 detectors = kwargs.get("detectors", {}),
                                 species = kwargs.get("species", {}))
    if tracetype == "datasc" or tracetype == "gctrace":
        _trace, _common = datasc.process(fn, **kwargs)
#    elif tracetype == "chromtab":
#        _ts, _meta, _comm = chromtab.process(fn, **kwargs)
#    elif tracetype == "fusion":
#        _ts, _meta, _comm = fusion.process(fn, **kwargs)
    print(_trace.keys())
    for t in _trace["traces"]:
        print(len(t["x"]), len(t["y"]))
        print(t["x"][40], t["y"][40])
    for name, spec in calib.items():
        print(name)
        xseries = [ufloat(*i) for i in _trace["traces"][spec["id"]]["x"]]
        yseries = [ufloat(*i) for i in _trace["traces"][spec["id"]]["y"]]
        peaks = _find_peaks(xseries, yseries, spec["peakdetect"])

        areas = _integrate_peaks(xseries, yseries, peaks, spec["species"])
    assert False
        
        
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
            
