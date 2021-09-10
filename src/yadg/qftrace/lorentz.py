import numpy as np
import math
from scipy.optimize import curve_fit

import matplotlib
import matplotlib.pyplot as plt

def _lorentz(x, a, x0, gam, c):
    #return (a/(math.pi*gam)*(gam**2/((x - x0)**2 + gam**2)) + c
    #return (2 * a/math.pi) * (gam/(4*(x - x0)**2 + gam**2)) + c
    return a*(gam**2/((x-x0)**2 + gam**2)) + c

def prune(p0, freq, comp, absl, **kwargs):
    grad = np.gradient(absl)
    pruned = []
    min_v = absl[p0]
    min_g = grad[p0]
    threshold = 1e-4
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
    #absl = [max(absl) - a for a in absl]
    
    popt, pcov = curve_fit(_lorentz, freq, absl, p0=[-0.5, freq[absl.index(min(absl))], 1e5, 1])
    #print(popt)
    #plt.plot(freq, absl)
    #plt.plot(freq, [_lorentz(f, popt[0], popt[1], popt[2], popt[3]) for f in freq])
    #plt.show()
    return popt[1]/popt[2], popt[1]
