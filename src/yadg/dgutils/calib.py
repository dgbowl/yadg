from uncertainties import ufloat, UFloat
from typing import Union

_default_calib = {"linear": {"slope": 1.0, "intercept": 0.0}, "atol": 0, "rtol": 1e-3}


def _linear(x: UFloat, calspec: dict) -> UFloat:
    c = calspec.get("intercept", 0.0)
    m = calspec.get("slope", 1.0)
    y = m * x + c
    return y


def _inverse(y: UFloat, calspec: dict) -> UFloat:
    c = calspec.get("intercept", 0.0)
    m = calspec.get("slope", 1.0)
    x = (y - c) / m
    return x


def _poly(x: UFloat, calspec: dict) -> UFloat:
    y = 0
    for k, v in calspec.items():
        if k == "c":
            y += v
        elif k.startswith("c"):
            o = int(k[1:])
            y += v * (x ** o)
    return y


def calib_handler(
    x: Union[float, UFloat], calib: dict = None, atol: float = 0.0, rtol: float = 0.0
) -> UFloat:
    """
    Calibration handling function
    """
    if not isinstance(x, UFloat):
        x = ufloat(x, 0.0)
    if calib is None:
        calib = _default_calib
    if x.n == 0.0 and calib.get("forcezero", True):
        return x
    if "linear" in calib:
        y = _linear(x, calib["linear"])
    elif "inverse" in calib:
        y = _inverse(x, calib["inverse"])
    elif "polynomial" in calib:
        y = _poly(x, calib["polynomial"])
    elif "poly" in calib:
        y = _poly(x, calib["poly"])
    y = ufloat(
        y.n, max(y.s, calib.get("atol", atol), abs(y.n * calib.get("rtol", rtol)))
    )
    return y
