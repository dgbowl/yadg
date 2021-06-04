import numpy as np
from scipy import constants as const

def Qf2σ(Qs, Q0, fs, f0, Vs, Vc, A = 1, B = 2, C = 0.07, delta = 1):
    p = {}
    p["ε'p"] = (1 / A) * C * (Vc/Vs) * ((f0 - fs)/fs) + 1
    p["ε'b"] = ((p["ε'p"]**(1/3) - 1)/delta + 1)**3
    p['ε"p'] = (1 / B) * C * (Vc/Vs) * (1/Qs - 1/Q0)
    p['ε"b'] = (p['ε"p']/delta) * (p["ε'b"]/p["ε'p"])**(2/3)
    p["σ"] = p['ε"b'] * const.epsilon_0 * fs * 2 * np.pi
    return p
