import numpy as np
from scipy.optimize import curve_fit
import uncertainties as uc


def fit(fvals, fsigs, gvals, absgvals, **kwargs):
    """
    Naive fit.

    This fit finds the central frequency f0, finds the half-maximum (HM) by linear interpolation, and returns Q ~ f0 / FWHM.
    """
    maxg = absgvals.max()
    ming = absgvals.min()
    absgamma = (absgvals - maxg) / (ming - maxg)
    ai = np.argmax(absgamma)
    lf = np.interp(0.5, absgamma[:ai], fvals[:ai])
    rf = np.interp(0.5, absgamma[ai:][::-1], fvals[ai:][::-1])
    f0 = uc.ufloat(fvals[ai], fsigs[ai])
    return f0 / (uc.ufloat(rf, fsigs[ai]) - uc.ufloat(lf, fsigs[ai])), f0
