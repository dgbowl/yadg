"""
Quality factor fitting routines.

.. _parsers_qftrace_methods:

List of supported quality factor fitting methods:

 - Naive fitting using half-width-half-maximum around the minimum of 
   :math:`|\\Gamma(f)|` in :func:`yadg.parsers.qftrace.fit.naive`
 - Lorentzian fit to the trace of :math:`|\\Gamma(f)|` trimmed using a 
   gradient threshold criterium in :func:`yadg.parsers.qftrace.fit.lorentz`
 - Kajfez's circle fitting routine to :math:`\\Gamma(f)`, using a peak-height 
   cutoff pruning method in :func:`yadg.parsers.qftrace.fit.kajfez`

Kajfez's method is the preferred one and hence set as default, with a ``cutoff``
set to 0.4.

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""
import numpy as np
from scipy.optimize import curve_fit
import uncertainties as uc


def naive(
    fvals: np.ndarray,
    fsigs: np.ndarray,
    gvals: np.ndarray,
    absgvals: np.ndarray,
    **kwargs: dict
) -> tuple[uc.ufloat, uc.ufloat]:
    """
    Naive fitting routine.

    This fit finds the central frequency :math:`f_0`, determines the full-width at
    the half-maximum :math:`\\Delta f_{HM}` by linear interpolation, and calculates
    the quality factor using :math:`Q_0 = f_0 / \\Delta f_{HM}`.

    - This fit first normalises the :math:`|\\Gamma(f)|` trace to values between 0 and 1.
    - The trace is flipped in this process, obtaining :math:`||\\Gamma(f)||`.
    - The :math:`f_0` is determined by finding the frequency corresponding to the
      minimum in :math:`|\\Gamma(f)|` (that is, the maximum of :math:`||\\Gamma(f)||`).
    - The full-width-half-maximum (:math:`\\Delta f_{HM}`) value of the peak is then
      determined using linear interpolation of the trace, by difference of the :math:`f`
      at the two points where :math:`||\\Gamma(f)|| = 0.5`.
    - Finally, the quality factor is calculated from :math:`Q_0 = f_0 / \\Delta f_{HM}`.

    Parameters
    ----------
    fvals
        Nominal values of the frequencies
    fsigs
        Error values of the frequencies
    gvals
        Not used
    absgvals
        Absolute values of the reflection coefficient, :math:`|\\Gamma(f)|`

    Returns
    -------
    (Q0, f0): tuple[uc.ufloat, uc.ufloat]
        Fitted quality factor and central frequency of the data.
    """

    maxg = absgvals.max()
    ming = absgvals.min()
    absgamma = (absgvals - maxg) / (ming - maxg)
    ai = np.argmax(absgamma)
    lf = np.interp(0.5, absgamma[:ai], fvals[:ai])
    rf = np.interp(0.5, absgamma[ai:][::-1], fvals[ai:][::-1])
    f0 = uc.ufloat(fvals[ai], fsigs[ai])
    Q0 = f0 / (uc.ufloat(rf, fsigs[ai]) - uc.ufloat(lf, fsigs[ai]))
    return Q0, f0


def _lorentz(x, a, x0, gam, c):
    return a * (gam ** 2 / ((x - x0) ** 2 + gam ** 2)) + c


def lorentz(
    fvals: np.ndarray,
    fsigs: np.ndarray,
    gvals: np.ndarray,
    absgvals: np.ndarray,
    **kwargs: dict
) -> tuple[uc.ufloat, uc.ufloat]:
    """
    Lorentz fit.

    Fits a Lorentz function to the pruned data. The :math:`f_0 = x_0`, and the
    :math:`Q_0` is calculated from :math:`x_0 / \\Delta x = x_0 / (2\\gamma)`.

    - This fit starts by fitting a Lorentzian curve in the form
      :math:`L(x) = a \\frac{\\gamma^2}{(x - x_0)^2 + \\gamma^2} + c` to the
      :math:`|\\Gamma(f)|` trace, obtaining four parameters (:math:`a, x_0, \\gamma, c`).
    - The central frequency :math:`f_0` is simply :math:`x_0`.
    - The width of the Lorentzian is given by :math:`\\Delta x = 2\\gamma`.
    - The quality factor is determined using :math:`Q_0 = x_0 / \\Delta x`
    - Uncertainties of :math:`f_0` and :math:`Q_0` are calculated using the
      covariance matrix of the fit of :math:`L(x)` to :math:`|\\Gamma(f)|`.


    Parameters
    ----------
    fvals
        Nominal values of the frequencies
    fsigs
        Not used
    gvals
        Not used
    absgvals
        Absolute values of the reflection coefficient, :math:`|\\Gamma(f)|`

    Returns
    -------
    (Q0, f0): tuple[uc.ufloat, uc.ufloat]
        Fitted quality factor and central frequency of the data.
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
    x0 = uc.ufloat(popt[1], perr[1])
    gam = uc.ufloat(popt[2], perr[2])

    return x0 / (2 * gam), x0


def kajfez(
    fvals: np.ndarray,
    fsigs: np.ndarray,
    gvals: np.ndarray,
    absgvals: np.ndarray,
    **kwargs: dict
) -> tuple[uc.ufloat, uc.ufloat]:
    """
    Kajfez's circle-fitting program.

    Adapted from Q0REFL.m, which is a part of Kajfez, D.: "Linear fractional curve
    fitting for measurement of high Q factors", IEEE Trans. Microwave Theory Techn.
    42 (1994) 1149-1153.

    This fitting process attempts to fit a circle to a near-circular section of
    points on a Smith's chart. It's robust, quick, and reliable, and produces
    reasonable error estimates.

    Parameters
    ----------
    fvals
        Nominal values of the frequencies
    fsigs
        Error values of the frequencies
    gvals
        Complex reflection coefficient values, :math:`\\Gamma(f)`.
    absgvals
        Absolute values of the reflection coefficient, :math:`|\\Gamma(f)|`

    Returns
    -------
    (Q0, f0): tuple[uc.ufloat, uc.ufloat]
        Fitted quality factor and central frequency of the data.
    """
    niter = kwargs.get("iterations", 5)
    fre = fvals
    n = fvals.size
    gam1 = gvals
    agam1 = absgvals
    dia = agam1.min()
    idia = np.argmax(agam1)
    f0 = fre[idia]
    ena = np.ones(n)
    sig = np.ones(3)
    eps = np.ones(n)
    p = np.zeros(n)
    for ite in range(niter):
        x = 2 * (fre / f0 - ena)
        e3 = gam1 * x
        e2 = -ena
        e1 = -x
        F = -gam1
        x2 = abs(x) ** 2
        ga2 = abs(gam1) ** 2
        if ite == 0:
            p = 1.0 / (x2 * (ena + ga2) + ena)
        else:
            p = sig[1] ** 2 / (
                x2 * sig[0] ** 2 + sig[1] ** 2 + (x2 * ga2) * sig[2] ** 2
            )
        E = np.array([e1, e2, e3]).T
        PE = np.array([p * e1, p * e2, p * e3]).T
        C = E.conj().T @ PE  # @?
        q1 = E.conj().T @ (p * F)  # @ ?
        D = np.linalg.inv(C)
        g = D @ q1
        eps = g[0] * e1 + g[1] * e2 + g[2] * e3 - F
        S1sq = eps.conj().T @ (p * eps)
        Fsq = F.conj().T @ (p * F)
        sumden = C[0, 0] * D[0, 0] + C[1, 1] * D[1, 1] + C[2, 2] * D[2, 2]
        for m in range(3):
            sig[m] = np.sqrt(abs(D[m, m] * S1sq / sumden))
        diam1 = 2 * abs(g[1] * g[2] - g[0]) / abs(g[2].conj() - g[2])
        gamc1 = (g[2].conj() * g[1] - g[0]) / (g[2].conj() - g[2])
        gamd1 = g[0] / g[2]
        gam1L2 = 2 * gamc1 - gamd1
        delt = (g[1] - gam1L2) / (gam1L2 * g[2] - g[0])
        f0 = f0 * (1 + 0.5 * delt.real)
    f011 = f0
    dia1 = 2 * abs(g[1] * g[2] - g[0]) / abs(g[2].conj() - g[2])
    flin = np.linspace(fre[0], fre[-1], 201)
    ft = 2 * (flin / f011 - 1)
    gam1com = (g[0] * ft.T + g[1]) / (g[2] * ft.T + 1)
    gam1d = g[0] / g[2]
    gam1c = (g[2].conj() * g[1] - g[0]) / (g[2].conj() - g[2])
    QL1 = g[2].imag

    # QL1 -> Q01
    ang1 = -np.arctan2((-gam1d).imag, (-gam1d).real)
    ang2 = np.arctan2((gam1c - gam1d).imag, (gam1c - gam1d).real)
    angtot = ang1 + ang2
    cob = np.cos(angtot)
    rr2 = (1 - abs(gam1d) ** 2) * 0.5 / (1 - abs(gam1d) * cob)
    dr2 = 2 * rr2
    rr1 = dia1 * 0.5
    coupls = (1 / rr2 - 1) / (1 / rr1 - 1 / rr2)
    rs = 2 / dr2 - 1
    kapa1 = rr1 / (rr2 - rr1)
    Q01 = QL1 * (1 + kapa1)

    # standard deviations
    sdQL1 = np.sqrt((sig[2].real) ** 2 + sig[2] ** 2)
    sddia1an = np.sqrt(
        sig[0] ** 2 * abs(g[2]) ** (-2)
        + sig[1] ** 2
        + abs(g[0] / (g[2] ** 2)) ** 2 * sig[2] ** 2
    )
    equi = abs(gam1 - gamc1)
    avequi = equi.mean()
    sdequi = equi.std()
    sddia1st = sdequi * 2
    sddia1 = sddia1an
    sdkapa1 = sddia1 / (2 - dia1) ** 2
    sdQ01 = np.sqrt((1 + kapa1) ** 2 * sdQL1 ** 2 + QL1 ** 2 * sdkapa1 ** 2)

    return uc.ufloat(Q01, sdQ01), uc.ufloat(f011, fsigs[idia])
