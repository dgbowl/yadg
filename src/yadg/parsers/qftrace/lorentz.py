from uncertainties import ufloat
import numpy as np
from scipy.optimize import curve_fit


def _lorentz(x, a, x0, gam, c):
    return a * (gam ** 2 / ((x - x0) ** 2 + gam ** 2)) + c


def fit(freq, gamma, absgamma, **kwargs):
    """
    Lorentz fit.

    Fits a Lorentz function to the pruned data. The f0 is approximated as x0, and the Q is calculated from Q ~ f0 / FWHM = x0 / (2γ)
    """
    popt, pcov = curve_fit(
        _lorentz,
        [i.n for i in freq],
        [i.n for i in absgamma],
        sigma=[i.s for i in absgamma],
        absolute_sigma=True,
        p0=[-0.5, freq[np.argmin(absgamma)].n, 1e5, 1],
    )
    perr = np.sqrt(np.diag(pcov))
    x0 = ufloat(popt[1], perr[1]*popt[1])
    gam = ufloat(popt[2], perr[2]*popt[2])

    return x0 / (2 * gam), x0
