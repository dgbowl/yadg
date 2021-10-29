import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat, unumpy


def fit(freq, gamma, absgamma, **kwargs):
    """
    Naive fit.

    This fit finds the central frequency f0, finds the half-maximum (HM) by linear interpolation, and returns Q ~ f0 / FWHM.
    """
    maxg = absgamma.max()
    ming = absgamma.min()
    absgamma = (absgamma - maxg) / (ming - maxg)
    ai = np.argmax(absgamma)
    lf = np.interp(
        0.5, unumpy.nominal_values(absgamma[:ai]), unumpy.nominal_values(freq[:ai])
    )
    rf = np.interp(
        0.5,
        unumpy.nominal_values(absgamma[ai:][::-1]),
        unumpy.nominal_values(freq[ai:][::-1]),
    )
    f0 = freq[ai]
    return f0 / (ufloat(rf, f0.s) - ufloat(lf, f0.s)), f0
