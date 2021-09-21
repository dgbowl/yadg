import numpy as np

def cutoff(p0, freq, gamma, absgamma, cutoff):
    """
    Cutoff-based prune.
    """
    min_v = absgamma[p0]
    max_v = max(absgamma)
    for l in range(p0 - 1):
        li = p0 - l
        norm = (absgamma[li] - min_v) / (max_v - min_v)
        if norm <= cutoff:
            pass
        else:
            break
    for r in range(len(absgamma) - p0):
        ri = p0 + r
        norm = (absgamma[ri] - min_v) / (max_v - min_v)
        if norm <= cutoff:
            pass
        else:
            break
    return freq[li+1:ri-1], gamma[li+1:ri-1], absgamma[li+1:ri-1]

def gradient(p0, freq, gamma, absgamma, threshold):
    """
    Gradient-based prune.
    """
    grad = np.gradient([i.n for i in absgamma])
    for l in range(p0-1):
        li = p0 - l
        if abs(grad[li]) > threshold or l < 100:
            pass
        else:
            break
    for r in range(len(absgamma) - p0):
        ri = p0 + r
        if abs(grad[ri]) > threshold or r < 100:
            pass
        else:
            break
    return freq[li+1:ri-1], gamma[li+1:ri-1], absgamma[li+1:ri-1]