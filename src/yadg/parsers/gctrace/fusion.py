import logging
import json
import numpy as np
import dgutils

def process(fn: str, encoding: str, atol: float = 0.0, rtol: float = 0.0,
            **kwargs: dict) -> tuple[list, dict, dict]:
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and pre-analysed results.
    Only a subset of the metadata is retained, including the method name,
    detector names, and information about assigned peaks.
    """
    with open(fn, "r", encoding = encoding, errors="ignore") as infile:
        jsdata = json.load(infile)

    metadata = {
        "type": "gctrace.fusion",
        "gcparams": {
            "method": jsdata.get("methodName", ""),
            "sampleid": jsdata.get("annotations", {}).get("name", ""),
            "valve": {
                "valvename": jsdata.get("annotations", {}).get("valcoPositionName", ""),
                "valveid": jsdata.get("annotations", {}).get("valcoPosition", None)
            },
            "version": jsdata.get("softwareVersion", {}).get("version", "")
        }
    }
    common = {}
    _, datefunc = dgutils.infer_timestamp_from([], 
                            spec = {"timestamp": {"format": "%Y-%m-%dT%H:%M:%S.%fZ"}})
    chrom = {
        "fn": str(fn), 
        "traces": [],
        "uts": datefunc(jsdata["runTimeStamp"]),
        "detectors": {}
    }
    detid = 0
    for detname in sorted(jsdata["detectors"].keys()):
        chrom["detectors"][detname] = {"id": detid}
        detid += 1
        detdict = jsdata["detectors"][detname]
        trace = {"x": [], "y": []}
        xmul = detdict["nValuesPerSecond"]
        npoints = detdict["nValuesExpected"]
        assert len(detdict["values"]) == npoints, \
            logging.error(f"fusion: Inconsistent trace length in file {fn}.")
        xs = np.linspace(0, npoints/xmul, num=npoints)
        xtol = max(0.5 * 1/xmul, atol, rtol * max(xs))
        ytol = max(1.0, atol, rtol * max(detdict["values"]))
        trace["x"] = [[x, xtol, "s"] for x in xs]
        trace["y"] = [[float(y), ytol, "-"] for y in detdict["values"]]
        if "analysis" in detdict:
            trace["peaks"] = {}
            for peak in detdict["analysis"]["peaks"]:
                if "label" not in peak:
                    continue
                if "baselinePoints" in peak:
                    nbp = peak["baselinePoints"]["start"] - peak["baselinePoints"]["end"]
                else:
                    nbp = 0
                h = [float(peak.get("height", 0.0)), 0.5, "-"]
                A = [float(peak.get("area", 0.0)), 0.5 * nbp, "-"]
                c = [float(peak.get("concentration", 0.0)), 0.0, "vol%"]
                trace["peaks"][peak["label"]] = {"h": h, "A": A, "c": c}
        chrom["traces"].append(trace)
        
    return [chrom], metadata, common
    

