import json
from scipy.signal import find_peaks, savgol_filter
import numpy as np
import logging
import uncertainties as uc
import uncertainties.unumpy as unp

from yadg.parsers.gctrace import datasc, chromtab, fusion
import yadg.dgutils

version = "1.0.dev1"


def _get_smooth_yvals(yvals: np.ndarray, pd: dict) -> np.ndarray:
    """
    Wrapper around :func:`scipy.signal.savgol_filter`. If the window length and the
    polynomial order are specified in ``pd``, the smoothened ``yvals`` are returned.
    Otherwise, the original ``yvals`` are returned.

    The function also validates that the specified window length derived from the
    ``"window"`` is larger than the ``"polyorder"``.
    """
    if pd.get("polyorder", None) is None or pd.get("window", None) is None:
        logging.info("gctrace: no smoothing.")
        return yvals
    else:
        window = pd.get("window", 3) * 2 + 1
        polyorder = pd.get("polyorder", 3)
        assert polyorder < window, f"gctrace: specified window <= polyorder."
        if polyorder == 2:
            logging.warning(
                "gctrace: smoothing with a polyorder == 2 can be unreliable. "
                "Consider switching to a higher polyorder or disabling smoothing "
                "completely."
            )
        return savgol_filter(yvals, window_length=window, polyorder=polyorder)


def _find_peak_maxima(yvals: np.ndarray, pd: dict) -> dict:
    """
    This function is a wrapper around :func:`scipy.signal.find_peaks` as well as
    a helper finding the points at which the gradient and Hessian of ``yvals``
    is zero (maxima, minima, inflection points).
    """
    # find positive and negative peak indices
    peaks = {}
    res, _ = find_peaks(yvals, prominence=pd.get("prominence", 1e-4 * yvals.max()))
    peaks["+"] = res
    res, _ = find_peaks(yvals * -1, prominence=pd.get("prominence", 1e-4 * yvals.max()))
    peaks["-"] = res
    # gradient: find peaks and inflection points
    grad = np.gradient(yvals)
    res = np.nonzero(np.diff(np.sign(grad)))[0] + 1
    peaks["gradzero"] = res
    # hessian: find peaks
    hess = np.gradient(grad)
    res = np.nonzero(np.diff(np.sign(hess)))[0] + 1
    peaks["hesszero"] = res
    return peaks


def _find_peak_edges(yvals: np.ndarray, peakdata: dict, detector: dict) -> dict:
    """
    A function that, given the y-values of a trace in ``yvals`` and the maxima,
    inflection points etc. in ``peakdata``, and the peak integration `"threshold"`
    in ``detector``, finds the edges ``"llim"`` and ``"rlim"`` of each peak.
    """
    threshold = detector.get("threshold", 1.0)
    allpeaks = []
    for pi in range(len(peakdata["+"])):
        pmax = peakdata["+"][pi]
        for i in range(len(peakdata["hesszero"])):
            if peakdata["hesszero"][i] > pmax:
                hi = i
                break
        for i in range(len(peakdata["gradzero"])):
            if peakdata["gradzero"][i] > pmax:
                gi = i
                break
        # right of peak:
        rlim = False
        rmin = False
        rthr = False
        rhi = False
        for xi in range(peakdata["hesszero"][hi], yvals.size):
            if xi in peakdata["gradzero"] and not rmin:
                rmin = xi
            elif xi in peakdata["hesszero"][hi:]:
                if rhi:
                    dx = xi - rhi
                    dy = yvals[xi] - yvals[rhi]
                    if abs(dy / dx) < threshold and not rthr:
                        rthr = xi
                rhi = xi
            if rthr and rmin:
                break
        rlim = min(rthr if rthr else yvals.size, rmin if rmin else yvals.size)
        if rlim == yvals.size:
            logging.warning("gctrace: possible mismatch of peak end.")
            rlim -= 1
        # left of peak
        lmin = False
        lthr = False
        lhi = False
        for xi in range(0, peakdata["hesszero"][hi - 1])[::-1]:
            if xi in peakdata["gradzero"] and not lmin:
                lmin = xi
            if xi in peakdata["hesszero"][: hi - 1]:
                if lhi:
                    dx = xi - lhi
                    dy = yvals[xi] - yvals[lhi]
                    if abs(dy / dx) < threshold and not lthr:
                        lthr = xi
                lhi = xi
            if lthr and lmin:
                break
        llim = max(lthr if lthr else 0, lmin if lmin else 0)
        if llim == 0:
            logging.warning("gctrace: possible mismatch of peak start.")
        allpeaks.append({"llim": llim, "rlim": rlim, "max": pmax})
    return allpeaks


def _get_baseline(ys: list[np.ndarray], peakdata: dict) -> list[np.ndarray]:
    """
    Function that returns a baseline based on the trace defined by ``ys``. The
    baseline is created by a linear interpolation between the ``"llim"`` and
    ``"rlim"`` of each `peak` in ``peakdata``. Returns the corrected baseline.
    """
    interpolants = []
    for p in peakdata:
        if len(interpolants) == 0:
            interpolants.append([p["llim"], p["rlim"]])
        else:
            if interpolants[-1][1] == p["llim"]:
                interpolants[-1][1] = p["rlim"]
            else:
                interpolants.append([p["llim"], p["rlim"]])
    bn = ys[0].copy()
    bs = ys[1].copy()
    for pair in interpolants:
        n = pair[1] - pair[0]
        interp = np.interp(range(n), [0, n], [bn[pair[0]], bn[pair[1]]])
        bn[pair[0] : pair[1]] = interp
        bs[pair[0] : pair[1]] = np.zeros(n)
    return bn, bs


def _integrate_peaks(
    xs: list[np.ndarray],
    ys: list[np.ndarray],
    peakdata: dict,
    specdata: dict,
) -> dict:
    """
    A function which, given a trace in [`xs`, `ys`], `peakdata` containing the boundaries
    `"llim"` and `"rlim"` for each `peak`, and `specdata` containing the peak-maximum
    matching limits `"l"` and `"r"`, first assigns peaks into `truepeaks`, then
    baseline-corrects [`xs`, `ys`], and finally integrates the peaks using numpy.trapz().
    """
    xsn = xs[0]
    truepeaks = {}
    for name, species in specdata.items():
        for p in peakdata:
            if xsn[p["max"]] > species["l"] and xsn[p["max"]] < species["r"]:
                truepeaks[name] = p
                break
    bln = _get_baseline(ys, peakdata)
    for k, v in truepeaks.items():
        s = v["llim"]
        e = v["rlim"] + 1
        py = unp.uarray(ys[0][s:e] - bln[0][s:e], ys[1][s:e] - bln[1][s:e])
        px = unp.uarray(xs[0][s:e], xs[1][s:e])
        A = np.trapz(py, px)
        truepeaks[k]["A"] = A
        truepeaks[k]["h"] = py[v["max"] - s]
    return truepeaks


def _parse_detector_spec(
    calfile: str = None, detectors: dict = None, species: dict = None
) -> dict:
    """
    Combines the GC spec from the json file specified in `calfile` with the dict
    definitions provided in `detectors` and `species`.
    """
    if calfile is not None:
        with open(calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if isinstance(detectors, dict):
        for name, det in detectors.items():
            try:
                calib[name].update(det)
            except KeyError:
                calib[name] = det
    if isinstance(species, dict):
        for name, sp in species.items():
            assert name in calib, (
                f"gctrace: Detector with name {name} specified in supplied "
                f"'species' but previously undefined."
            )
            try:
                calib[name]["species"].update(sp)
            except KeyError:
                calib[name]["species"] = sp
    return calib


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    tracetype: str = "datasc",
    detectors: dict = None,
    species: dict = None,
    calfile: str = None,
) -> tuple[list, dict, dict]:
    """
    GC chromatogram parser.

    This parser processes GC chromatograms in signal(time) format. When provided
    with a calibration file, this tool will integrate the trace, and provide the
    peak areas, retention times, and concentrations of the detected species.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    tracetype
        Determines the output file format. Currently supported formats are
        ``"chromtab"`` (), ``"datasc"`` (EZ-Chrom ASCII export), ``"fusion"`` (Fusion
        json file). The default is ``"datasc"``.

    detectors
        Detector specification. Matches and identifies a trace in the `fn` file.
        If provided, overrides data provided in ``calfile``, below.

    species
        Species specification. Per-detector species can be listed here, providing an
        expected retention time range for the peak maximum. Additionally, calibration
        data can be supplied here. Overrides data provided in ``calfile``, below.

    calfile
        Path to a json file containing the ``detectors`` and ``species`` spec. Either
        ``calfile`` and/or ``species`` and ``detectors`` have to be provided.

    Returns
    -------
    (data, metadata, common) : tuple[list, dict, None]
        Tuple containing the timesteps, metadata, and common data.
    """
    assert calfile is not None or (species is not None and detectors is not None), (
        "gctrace: Neither 'calfile' nor both 'species' and 'detectors' were provided. "
        "Fit cannot proceed."
    )
    gcspec = _parse_detector_spec(calfile, detectors, species)
    if tracetype == "datasc" or tracetype == "gctrace":
        _data, _meta, _common = datasc.process(fn, encoding, timezone)
    elif tracetype == "chromtab":
        _data, _meta, _common = chromtab.process(fn, encoding, timezone)
    elif tracetype == "fusion":
        _data, _meta, _common = fusion.process(fn, encoding, timezone)
    results = []
    for chrom in _data:
        peaks = {}
        comp = []
        for detname, spec in gcspec.items():
            for det in chrom["traces"].keys():
                if chrom["traces"][det]["id"] == spec["id"]:
                    chrom["traces"][det]["calname"] = detname
                    break
            units = {
                "x": chrom["traces"][det]["x"]["u"],
                "y": chrom["traces"][det]["y"]["u"],
                "A": "-",
            }
            xs, ys = chrom["traces"][det].pop("data")
            pd = spec.get("peakdetect", {})
            smooth = _get_smooth_yvals(ys[0], pd)
            peakmax = _find_peak_maxima(smooth, pd)
            peakspec = _find_peak_edges(smooth, peakmax, pd)
            integrated = _integrate_peaks(xs, ys, peakspec, spec["species"])
            peaks[detname] = {}
            for k, v in integrated.items():
                peaks[detname][k] = {
                    "peak": {
                        "max": int(v["max"]),
                        "llim": int(v["llim"]),
                        "rlim": int(v["rlim"]),
                    },
                    "A": {"n": v["A"].n, "s": v["A"].s, "u": units["A"]},
                    "h": {"n": v["h"].n, "s": v["h"].s, "u": units["y"]},
                }
                if spec["species"][k].get("calib", None) is not None:
                    x = yadg.dgutils.calib_handler(v["A"], spec["species"][k]["calib"])
                    x = max(uc.ufloat(0.0, x.s), x)
                    peaks[detname][k]["c"] = {
                        "n": x.n,
                        "s": x.s,
                        "u": spec["species"][k]["calib"].get("unit", "vol%"),
                        "uf": x,
                    }
                if k not in comp:
                    comp.append(k)
        xout = {}
        for s in comp:
            for d, ds in gcspec.items():
                if s in peaks[d] and "c" in peaks[d][s]:
                    v = peaks[d][s]["c"].pop("uf")
                    if ds.get("prefer", False) or s not in xout:
                        xout[s] = v
        norm = sum([xout[k] for k in xout.keys()])
        for s in xout:
            xnorm = xout[s] / norm
            xout[s] = {"n": xnorm.n, "s": xnorm.s, "u": "-"}
        result = {"uts": chrom.pop("uts"), "fn": chrom.pop("fn")}
        result["raw"] = chrom
        result["derived"] = {"peaks": peaks, "xout": xout}
        assert result["fn"] == fn
        results.append(result)

    return results, _meta, _common
