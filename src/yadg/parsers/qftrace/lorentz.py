from uncertainties import ufloat, unumpy
import numpy as np
from scipy.optimize import curve_fit


def _lorentz(x, a, x0, gam, c):
    return a * (gam ** 2 / ((x - x0) ** 2 + gam ** 2)) + c


def fit(fvals, fsigs, gvals, absgvals, **kwargs):
    """
    Lorentz fit.

    Fits a Lorentz function to the pruned data. The f0 is approximated as x0, and the Q is calculated from Q ~ f0 / FWHM = x0 / (2γ)
    """
    popt, pcov = curve_fit(
        _lorentz,
        fvals,
        absgvals,
        sigma=absgvals,
        absolute_sigma=True,
        p0=[-0.5, fvals[np.argmin(absgvals)], 1e5, 1],
    )
    perr = np.sqrt(np.diag(pcov))
    x0 = ufloat(popt[1], perr[1])
    gam = ufloat(popt[2], perr[2])

    return x0 / (2 * gam), x0
