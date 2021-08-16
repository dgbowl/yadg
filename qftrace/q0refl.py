import numpy as np
import math

def prune(p0, freq, comp, absl, **kwargs):
    cutoff = kwargs.get("cutoff", 0.4)
    pruned = []
    min_v = absl[p0]
    max_v = max(absl)
    pf = []
    pc = []
    for l in range(p0-1):
        li = p0 - l
        norm = (absl[li] - min_v) / (max_v - min_v)
        if norm <= cutoff:
            pf.insert(0, freq[li])
            pc.insert(0, comp[li])
        else:
            break
    for r in range(len(absl) - p0):
        ri = p0 + r
        norm = (absl[ri] - min_v) / (max_v - min_v)
        if norm <= cutoff:
            pf.append(freq[ri])
            pc.append(comp[ri])
        else:
            break
    return pf[1:-1], pc[1:-1]

def fit(freq, comp, **kwargs):
    iterations = kwargs.get("iterations", 5)
    indices = range(len(freq))
    p_freq = np.array(freq)
    p_c    = np.array(comp)
    p_abs  = np.array([abs(i) for i in comp])
    
    min_i = np.argmin(p_abs)
    min_freq = p_freq[min_i]
    
    f0 = min_freq
    ena = np.array([1]*len(freq))
    eps = np.array([1]*len(freq))
    p   = np.array([0]*len(freq))
    sig = [1,1,1]
    
    # circle fitting
    for ite in range(iterations):
        x = 2 * (p_freq / f0 - ena)
        e3 = np.multiply(p_c, x)
        e1 = -x
        e2 = -ena
        F = -p_c
        x2 = abs(x)**2
        ga2 = p_abs**2
        if ite == 1:
            p = 1/(np.multiply(x2, ena + ga2) + ena)
        else:
            p = sig[1]**2 / (x2 * sig[0]**2 + sig[1]**2 + np.multiply(x2, ga2) * sig[2]**2)
        E = np.matrix([e1,e2,e3]).T
        PE = np.matrix([np.multiply(p, e1), np.multiply(p, e2), np.multiply(p, e3)]).T
        C = np.matmul(E.H, PE)
        q1 = np.dot(E.H, np.multiply(p, F)).T
        D = C.I
        g = np.matmul(D, q1)
        eps = g[0] * e1 + g[1] * e2 + g[2] * e3  - F
        S1sq = np.matmul(eps, np.multiply(p, eps).H)
        Fsq = np.dot(F, np.multiply(p, F))
        
        sumden=C[0,0]*D[0,0] + C[1,1]*D[1,1] + C[2,2]*D[2,2]
        for m in [0,1,2]:
            sig[m] = math.sqrt(abs(D[m,m]*S1sq/sumden))
        
        diam1 = 2 * abs(g[1] * g[2] - g[0]) / abs(g[2].conjugate() - g[2])
        gamc1 = (g[2].conjugate() * g[1] - g[0]) / (g[2].conjugate() - g[2])
        gamd1 = g[0]/g[2]
        gam1L2 = 2 * gamc1 - gamd1
        delt = (g[1] - gam1L2) / (gam1L2 * g[2] - g[0])
        f0 = float(f0 * (1 + 0.5 * delt.real))
    
    f011 = f0
    dia1 = 2 * abs(g[1] * g[2] - g[0]) / abs(g[2].conjugate() - g[2])
    flin = np.linspace(p_freq[0], p_freq[-1], 201)
    ft = 2 * (flin / f011 - 1)
    gam1com = (g[0] * ft.T + g[1]) / (g[2] * ft.T + 1)
    gam1d = g[0]/g[2]
    gam1c = (g[2].conjugate() * g[1] - g[0]) / (g[2].conjugate() - g[2])
    QL1 = g[2].imag
    
    # QL1 -> Q01
    ang1 = -math.atan2((-gam1d).imag,(-gam1d).real)
    ang2 = math.atan2((gam1c-gam1d).imag, (gam1c-gam1d).real)
    angtot = ang1 + ang2
    cob = math.cos(angtot)
    rr2 = (1 - abs(gam1d)**2) * 0.5 / (1 - abs(gam1d) * cob)
    dr2 = 2 * rr2
    rr1 = dia1 * 0.5
    coupls = (1 / rr2 - 1) / (1 / rr1 - 1 / rr2)
    rs = 2 / dr2 - 1
    kapa1 = rr1 / (rr2 - rr1)
    Q01 = float(QL1 * (1 + kapa1))
    
    # standard deviations
    sdQL1 = math.sqrt((sig[2].real)**2 + sig[2]**2)
    sddia1an = math.sqrt(sig[0]**2 * abs(g[2])**(-2) + \
                        sig[1]**2 + \
                        abs(g[0]/(g[2]**2))**2 * sig[2]**2)
    equi = abs(p_c - gamc1)
    avequi = equi.mean()
    sdequi = equi.std()
    sddia1st = sdequi*2
    sddia1 = sddia1an
    sdkapa1 =  sddia1 / (2 - dia1)**2
    sdQ01 = math.sqrt((1 + kapa1)**2 * sdQL1**2 + QL1**2 * sdkapa1**2)
    
    return Q01, f011
