from uncertainties import ufloat
import numpy as np

def fit(freq, gamma, absgamma, **kwargs):
    """
    Kajfez's circle-fitting program.

    Adapted from Q0REFL.m, which is a part of Kajfez, D.: "Linear fractional curve 
    fitting for measurement of high Q factors", IEEE Trans. Microwave Theory Techn. 
    42 (1994) 1149-1153.

    This fitting process attempts to fit a circle to a near-circular section of 
    points on a Smith's chart. It's robust, quick, and reliable, and produces
    reasonable error estimates.
    """
    niter = kwargs.get("iterations", 5)
    fre = np.array([i.n for i in freq])
    n = len(fre)
    gam1 = np.array(gamma)
    agam1 = np.abs(gam1)
    dia = np.min(agam1)
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
        x2 = abs(x)**2
        ga2 = abs(gam1)**2
        if ite == 0:
            p = 1.0 / (x2 * (ena + ga2) + ena)
        else:
            p = sig[1]**2 / (x2 * sig[0]**2 + sig[1]**2 + (x2 * ga2) * sig[2]**2)
        E = np.array([e1, e2, e3]).T
        PE = np.array([p * e1, p * e2, p * e3]).T
        C = E.conj().T @ PE # @?
        q1 = E.conj().T @ (p * F) #@ ?
        D = np.linalg.inv(C)
        g = D @ q1
        eps = g[0] * e1 + g[1] * e2 + g[2] * e3 - F
        S1sq = eps.conj().T @ (p * eps)
        Fsq = F.conj().T @ (p * F)
        sumden = C[0,0] * D[0,0] + C[1,1] * D[1,1] + C[2,2] * D[2,2]
        for m in range(3):
            sig[m] = np.sqrt(abs(D[m,m] * S1sq/sumden))
        diam1 = 2 * abs(g[1] * g[2] - g[0]) / abs(g[2].conj() - g[2])
        gamc1 = (g[2].conj()*g[1] - g[0])/(g[2].conj() - g[2])
        gamd1 = g[0]/g[2]
        gam1L2 = 2 * gamc1 - gamd1
        delt = (g[1] - gam1L2)/(gam1L2 * g[2] -g[0])
        f0 = f0 * ( 1 + 0.5 * delt.real)
    f011 = f0
    dia1 = 2 * abs(g[1] * g[2] - g[0]) / abs(g[2].conj() - g[2])
    flin = np.linspace(fre[0], fre[-1], 201)
    ft = 2 * (flin / f011 - 1)
    gam1com = (g[0] * ft.T + g[1]) / (g[2] * ft.T + 1)
    gam1d = g[0]/g[2]
    gam1c = (g[2].conj() * g[1] - g[0]) / (g[2].conj() - g[2])
    QL1 = g[2].imag
    
    # QL1 -> Q01
    ang1 = -np.arctan2((-gam1d).imag, (-gam1d).real)
    ang2 = np.arctan2((gam1c-gam1d).imag, (gam1c-gam1d).real)
    angtot = ang1 + ang2
    cob = np.cos(angtot)
    rr2 = (1 - abs(gam1d)**2) * 0.5 / (1 - abs(gam1d) * cob)
    dr2 = 2 * rr2
    rr1 = dia1 * 0.5
    coupls = (1 / rr2 - 1) / (1 / rr1 - 1 / rr2)
    rs = 2 / dr2 - 1
    kapa1 = rr1 / (rr2 - rr1)
    Q01 = QL1 * (1 + kapa1)
    
    # standard deviations
    sdQL1 = np.sqrt((sig[2].real)**2 + sig[2]**2)
    sddia1an = np.sqrt(sig[0]**2 * abs(g[2])**(-2) + \
                       sig[1]**2 + \
                       abs(g[0]/(g[2]**2))**2 * sig[2]**2)
    equi = abs(gam1 - gamc1)
    avequi = equi.mean()
    sdequi = equi.std()
    sddia1st = sdequi*2
    sddia1 = sddia1an
    sdkapa1 =  sddia1 / (2 - dia1)**2
    sdQ01 = np.sqrt((1 + kapa1)**2 * sdQL1**2 + QL1**2 * sdkapa1**2)
    
    return ufloat(Q01, sdQ01), ufloat(f011, freq[idia].s)
 
