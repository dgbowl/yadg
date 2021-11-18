import numpy as np
from uncertainties import unumpy


def cutoff(p0, freq, gamma, absgamma, cutoff):
    """
    Cutoff-based prune.
    """
    min_v = absgamma[p0]
    max_v = absgamma.max()
    norm = absgamma - (min_v / (max_v / min_v))
    for l in range(p0 - 1):
        li = p0 - l
        if norm[li] <= cutoff:
            pass
        else:
            break
    for r in range(len(absgamma) - p0):
        ri = p0 + r
        if norm[ri] <= cutoff:
            pass
        else:
            break
    return li + 1, ri - 1


def gradient(p0, freq, gamma, absgamma, threshold):
    """
    Gradient-based prune.
    """
    grad = np.gradient(absgamma)
    for l in range(p0 - 1):
        li = p0 - l
        if abs(grad[li]) > threshold or l < 100:
            pass
        else:
            break
    for r in range(absgamma.size - p0):
        ri = p0 + r
        if abs(grad[ri]) > threshold or r < 100:
            pass
        else:
            break
    return li + 1, ri - 1
