import math
import sys
import matplotlib
import matplotlib.pyplot as plt
import peakutils
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter
from scipy.optimize import curve_fit
import numpy as np
import copy

def _peak_end_deriv(ydata, pi, tabs = 1E-5):
    dy = [ydata[i+1] - ydata[i] for i in range(len(ydata)-1)]
    ddy = [0] + [dy[i+1] - dy[i] for i in range(len(dy)-1)]
    l = pi - 1
    r = pi + 1
    while abs(ddy[l]) > tabs and l > 0:
        l -= 1
    while abs(ddy[r]) < tabs and r < len(ydata):
        r += 1
    l += 1
    r -= 1
    if l + 1 == pi or r - 1 == pi:
        success = False
    else:
        success = True
    return(success, l, r)

def _peak_end_maxval(ydata, pi, trel = 0.00001, tabs = 0.01):
    dy = min(tabs, trel * ydata[pi])
    l = pi - 1
    while (ydata[l + 1] - ydata[l] > dy) and ((ydata[pi] - dy) > ydata[l]) and l > 0:
        l -= 1
    r = pi + 1
    while (ydata[r - 1] - ydata[r] > dy) and ((ydata[pi] - dy) > ydata[r]) and r + 1  < len(ydata):
        r += 1
    l += 1
    r -= 1
    if l == 0 or r + 1 == len(ydata) or l == pi or r == pi:
        success = False
    else:
        success = True
    return(success, l, r)


def _peak_end_naive(ydata, pi):
    l = pi - 1
    while ydata[l] < ydata[l + 1] and l - 2 > 0:
        l -= 1
    l += 1
    r = pi + 1
    while ydata[r] < ydata[r - 1] and r + 2 < len(ydata):
        r += 1
    r -= 1
    if l - 2 <= 0 or r + 2 >= len(ydata) or l + 1 == pi or r - 1 == pi:
        success = False
    else:
        success = True
    return(success, l, r)

def lowpass(values, width = 10, cut=2):
    x = np.linspace(0,1,len(values))
    fval = np.fft.fft(values)
    filtered = np.array(np.fft.fft(np.minimum(values,cut)))
    filtered *= np.exp(-x**2/width) + np.exp(-(1-x)**2/width)
    temp = np.fft.ifft(filtered)
    return(temp)


def correct(times, values, alims, window = 3, poly = 2, prominence = 0.5, return_baseline = False):
    # 1. smooth raw values
    smooth = savgol_filter(values, window_length = window,
                                   polyorder = poly)
    # 2. find peaks
    peaks, _ = find_peaks(smooth, prominence=prominence)
    # 3. create baseline
    baseline = copy.deepcopy(smooth)
    original = [True]*len(baseline)
    # 4a. iterate over analytes
    analyteareas = []
    peaklimits = []
    for analyte in alims:
        lefts = []
        rights = []
        areas = []
    # 4b. go through all detected peaks
        for pi in peaks:
            pt = times[pi]
            pv = smooth[pi]
    # 4c. but only through selected baseline areas
            if pt >= analyte[0] and pt <= analyte[1]:
    # 5a. Peak fitting: first attempt is using tight tolerances for change in steps
                success, l, r = _peak_end_maxval(smooth, pi)
    # 5b. Peak fitting: second attempt looks for a minimum naively
                if not success:
                    success, l, r = _peak_end_naive(smooth, pi)
                    print(" Second filter")
    # 5c. Peak fitting: if all fails, skip peak.
                if not success:
                    print(" Not found")
                    continue
    # 6.  interpolate baseline, subtract, calculate peak areas
    # 6a. shrink baseline limits so that peaks won't overlap
                while not original[l]:
                    l += 1
                while not original[r]:
                    r -= 1
    # 6b. expand extrapolation limits so that we get a smooth baseline with geminal peaks
                bl = l
                while not original[bl-1]:
                    bl -= 1
                br = r
                while not original[br+1]:
                    br += 1
    # 6c. trim baseline so that linear interpolation values are not crossing the data
                success = False
                while not success:
                    success = True
                    ansatz = [0] * len(baseline)
                    for ii in range(bl, br):
                        ansatz[ii] = smooth[bl] + (smooth[br] - smooth[bl])*(float(ii-bl)/float(br-bl))
                    differences = [smooth[ii] - ansatz[ii] for ii in range(bl,br)]
                    positive = True if differences[pi-bl-1] > 0 else False
                    for i in range(len(differences)):
                        if positive:
                            success *= differences[i] >= 0
                        else:
                            success *= differences[i] <= 0
                        if not success:
                            if i < pi - bl:
                                bl += 1
                            else:
                                br -= 1
                            break
    # 7a. Integration: iterate over final l -> r, tag, keep peak limits
                peakarea = 0
                for ii in range(bl,br):
                    baseline[ii] = ansatz[ii]
                    original[ii] = False
                    if ii >= l and ii < r:
                        peakarea += smooth[ii] - baseline[ii]
                lefts.append(l)
                rights.append(r)
                areas.append(peakarea)
    # 7b. Integration: retain [l, r] for the highest peak area in baseline segment
        if len(areas) > 0:
            a, l, r = max(zip(areas, lefts, rights))
            peaklimits.append([l,r])
        else:
            peaklimits.append([0,0])
    # 7c. Numerical integration after baseline is finished
    if len(peaklimits) == len(alims):
        for analyte in peaklimits:
            currentarea = 0
            for i in range(analyte[0],analyte[1]):
                currentarea += values[i] - baseline[i]
            analyteareas.append(currentarea)
    # 8. return
    if return_baseline:
        return analyteareas, baseline
    else:
        return analyteareas
