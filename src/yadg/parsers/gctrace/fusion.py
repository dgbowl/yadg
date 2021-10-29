import logging
import json
import numpy as np
from uncertainties import unumpy

import yadg.dgutils


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and pre-analysed results. Only a subset of the metadata is retained, including the method name, detector names, and information about assigned peaks.
    """
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)

    metadata = {
        "type": "gctrace.fusion",
        "gcparams": {
            "method": jsdata.get("methodName", ""),
            "sampleid": jsdata.get("annotations", {}).get("name", ""),
            "valve": {
                "valvename": jsdata.get("annotations", {}).get("valcoPositionName", ""),
                "valveid": jsdata.get("annotations", {}).get("valcoPosition", None),
            },
            "version": jsdata.get("softwareVersion", {}).get("version", ""),
        },
    }

    common = {}
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"timestamp": {}}, timezone=timezone
    )
    chrom = {"fn": str(fn), "traces": {}, "uts": datefunc(jsdata["runTimeStamp"])}
    detid = 0
    for detname in sorted(jsdata["detectors"].keys()):
        detdict = jsdata["detectors"][detname]
        trace = {"x": [], "y": [], "id": detid}
        detid += 1
        xmul = detdict["nValuesPerSecond"]
        npoints = detdict["nValuesExpected"]
        assert (
            len(detdict["values"]) == npoints
        ), f"fusion: Inconsistent trace length in file {fn}."
        xs = unumpy.uarray(np.arange(npoints), np.ones(npoints) * 0.5) / xmul
        ys = unumpy.uarray(detdict["values"], np.ones(npoints))
        trace["x"] = {
            "n": list(unumpy.nominal_values(xs)),
            "s": list(unumpy.std_devs(xs)),
            "u": "s",
        }
        trace["y"] = {
            "n": list(unumpy.nominal_values(ys)),
            "s": list(unumpy.std_devs(ys)),
            "u": "s",
        }
        trace["data"] = [xs, ys]
        if "analysis" in detdict:
            trace["peaks"] = {}
            for peak in detdict["analysis"]["peaks"]:
                if "label" not in peak:
                    continue
                if "baselinePoints" in peak:
                    nbp = (
                        peak["baselinePoints"]["start"] - peak["baselinePoints"]["end"]
                    )
                else:
                    nbp = 0
                h = {"n": float(peak.get("height", 0.0)), "s": 0.5, "u": "-"}
                A = {"n": float(peak.get("area", 0.0)), "s": 0.5 * nbp, "u": "-"}
                c = {"n": float(peak.get("concentration", 0.0)), "s": 0.0, "u": "vol%"}
                trace["peaks"][peak["label"]] = {"h": h, "A": A, "c": c}
        chrom["traces"][detname] = trace

    return [chrom], metadata, common
