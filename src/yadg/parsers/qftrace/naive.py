import numpy as np
from scipy.optimize import curve_fit


def fit(freq, gamma, absgamma, **kwargs):
    """
    Naive fit.

    This fit finds the central frequency f0, finds the half-maximum (HM) by linear interpolation, and returns Q ~ f0 / FWHM.
    """
    maxg = max(absgamma)
    absgamma = [maxg - a for a in absgamma]
    maxg = max(absgamma)
    absgamma = [a / maxg for a in absgamma]
    ai = np.argmax(absgamma)
    lf = np.interp(0.5, [i.n for i in absgamma[:ai]], [i.n for i in freq[:ai]])
    rf = np.interp(
        0.5, [i.n for i in absgamma[ai:][::-1]], [i.n for i in freq[ai:][::-1]]
    )
    f0 = freq[ai]
    return f0 / (rf - lf), f0
