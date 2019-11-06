import numpy as np
import math
from scipy.optimize import curve_fit

import matplotlib
import matplotlib.pyplot as plt

def prune(p0, freq, comp, absl, **kwargs):
    grad = np.gradient(absl)
    pruned = []
    min_v = absl[p0]
    min_g = grad[p0]
    threshold = 1e-6
    pf = []
    pa = []
    for l in range(p0-1):
        li = p0 - l
        if abs(grad[li]) > threshold or l < 100:
            pf.insert(0, freq[li])
            pa.insert(0, absl[li])
        else:
            break
    for r in range(len(absl) - p0):
        ri = p0 + r
        if abs(grad[ri]) > threshold or r < 100:
            pf.append(freq[ri])
            pa.append(absl[ri])
        else:
            break
    return pf[1:-1], pa[1:-1]

def fit(freq, absl, **kwargs):
    absl = [max(absl) - a for a in absl]
    absl = [a/max(absl) for a in absl]
    ai = absl.index(max(absl))
    lf = np.interp(0.5, absl[:ai], freq[:ai])
    rf = np.interp(0.5, absl[ai:][::-1], freq[ai:][::-1])
    f0 = freq[ai]
    
    #plt.plot(freq, absl)
    #plt.plot([lf,rf], [0.5, 0.5])
    #plt.show()
    
    return f0/(rf-lf), f0
