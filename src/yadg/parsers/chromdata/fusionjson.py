"""
**fusionjson**: Processing Inficon Fusion json data format (json).
------------------------------------------------------------------

This is a fairly detailed data format, including the traces, the calibration applied,
and also the integrated peak areas and other processed information, which are parsed
by this module.

.. note ::

    To parse the raw trace data, use the :mod:`~yadg.parsers.chromtrace` module.

.. warning ::

    The detectors in the json files are not necessarily in a consistent order. To
    avoid inconsistent parsing of species which appear in both detectors, the
    detector keys are sorted. **Species present in both detectors** will be 
    **overwritten by the last detector** in alphabetical order.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      username: None
      version:  !!str
      datafile: !!str

.. codeauthor:: Peter Kraus
"""
import json
import logging
from ...dgutils.dateutils import str_to_uts

logger = logging.getLogger(__name__)


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and pre-analysed results.
    Only a subset of the metadata is retained, including the method name,
    detector names, and information about assigned peaks.

    Parameters
    ----------
    fn
        Filename to process.

    encoding
        Encoding used to open the file.

    timezone
        Timezone information. This should be ``"localtime"``.

    Returns
    -------
    ([chrom], metadata, fulldate): tuple[list, dict, bool]
        Standard timesteps, metadata, and date tuple.
    """

    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)
    metadata = {
        "filetype": "fusion.json",
        "params": {
            "method": jsdata.get("methodName", "n/a"),
            "version": jsdata.get("softwareVersion", {}).get("version", None),
            "datafile": jsdata.get("sequence", {}).get("location", None),
            "username": None,
        },
    }
    chrom = {"fn": str(fn), "raw": {}}
    chrom["uts"] = str_to_uts(jsdata["runTimeStamp"], timezone=timezone)

    valve = jsdata.get("annotations", {}).get("valcoPosition", None)
    if valve is not None:
        chrom["raw"]["valve"] = valve

    sampleid = jsdata.get("annotations", {}).get("name", None)
    if sampleid is not None:
        chrom["raw"]["sampleid"] = sampleid

    raw = {
        "height": {},
        "area": {},
        "concentration": {},
        "xout": {},
        "retention time": {},
    }

    # sort detector keys to ensure alphabetic order for ID matching
    for detname in sorted(jsdata["detectors"].keys()):
        detdict = jsdata["detectors"][detname]
        if "analysis" in detdict:
            for peak in detdict["analysis"]["peaks"]:
                if "label" not in peak:
                    continue
                if "height" in peak:
                    h = {"n": float(peak["height"]), "s": 1.0, "u": " "}
                    raw["height"][peak["label"]] = h
                if "area" in peak:
                    A = {"n": float(peak["area"]), "s": 0.01, "u": " "}
                    raw["area"][peak["label"]] = A
                if "concentration" in peak:
                    c = {
                        "n": float(peak["concentration"]),
                        "s": float(peak["concentration"]) * 1e-3,
                        "u": "%",
                    }
                    raw["concentration"][peak["label"]] = c
                if "normalizedConcentration" in peak:
                    x = {
                        "n": float(peak["normalizedConcentration"]),
                        "s": float(peak["normalizedConcentration"]) * 1e-3,
                        "u": "%",
                    }
                    raw["xout"][peak["label"]] = x
                if "top" in peak:
                    rt = {
                        "n": float(peak["top"]),
                        "s": 0.01,
                        "u": "s",
                    }
                    raw["retention time"][peak["label"]] = rt
        else:
            logger.warning("'analysis' of chromatogram not present in file '%s'", fn)

    for k in {"height", "area", "concentration", "xout", "retention time"}:
        if raw[k] == 0:
            del raw[k]

    chrom["raw"].update(raw)
    return [chrom], metadata, True
