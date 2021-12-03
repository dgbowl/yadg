"""
Trace-pruning routines.

To reduce the impact of baseline noise and  speed up the fitting of :math:`Q_0` to
the :math:`\\Gamma(f)` trace, only smaller sections of the trace are retained around
each minimum. Two routines for trace-pruning are provided:

- a height cutoff-based prune in :func:`yadg.parsers.qftrace.prune.cutoff`
- a gradient threshold-based prune in :func:`yadg.parsers.qftrace.prune.threshold`

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""

import numpy as np
from uncertainties import unumpy


def cutoff(p0: int, absgamma: np.ndarray, cutoff: float) -> tuple[int, int]:
    """
    Cutoff-based prune.

    Parameters
    ----------
    p0
        Index of the minimum of ``absgamma``.
    absgamma
        The :math:`|\\Gamma(f)|` data.
    cutoff
        Normalised height above which the trace is cut off.

    Returns
    -------
    tuple[int, int]
        A tuple of the left and right index of the trimmed trace.
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


def gradient(p0: int, absgamma: np.ndarray, threshold: float) -> tuple[int, int]:
    """
    Gradient-based prune.

    Parameters
    ----------
    p0
        Index of the minimum of ``absgamma``.
    absgamma
        The :math:`|\\Gamma(f)|` data.
    threshold
        Threshold of the gradient below which the trace is cut off.

    Returns
    -------
    tuple[int, int]
        A tuple of the left and right index of the trimmed trace.
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
