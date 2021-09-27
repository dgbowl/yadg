from helpers import dateutils
import logging
import json
import numpy as np

def _process_headers(headers, columns):
    res = {}
    _, datefunc = dateutils._infer_timestamp_from([], 
                            spec = {"timestamp": [0, "%d %b %Y %H:%M"]})
    assert len(headers) == len(columns), \
        logging.error(f"chromtab: The number of headers and columns "
                      f"do not match on line {lines.index(line)} of file {fn}.")
    assert "Date Acquired" in headers, \
        logging.error("chromtab: Cannot infer date.")
    res["uts"] = datefunc(columns[headers.index("Date Acquired")].strip())
    fn = ""
    if "Path" in headers:
        fn += columns[headers.index("Path")]
    if "File" in headers:
        fn += columns[headers.index("File")]
    res["datafile"] = fn
    if "Sample" in headers:
        res["sampleid"] = columns[headers.index("Sample")]
    return res

def process(fn, **kwargs):
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and pre-analysed results.
    """
    with open(fn, "r", encoding="utf8", errors="ignore") as infile:
        jsdata = json.load(infile)

    metadata = {
        "type": "gctrace.fusion",
        "gcparams": {
            "method": jsdata.get("methodName", "")
        }
    }
    common = {}
    _, datefunc = dateutils._infer_timestamp_from([], 
                            spec = {"timestamp": [0, "%Y-%m-%dT%H:%M:%S"]})
    chrom = {
        "fn": str(fn), 
        "traces": [],
        "uts": datefunc(jsdata["runTimeStamp"].split(".")[0])
    }
    for detname in sorted(jsdata["detectors"].keys()):
        detdict = jsdata["detectors"][detname]
        trace = {"x": [], "y": []}
        xmul = detdict["nValuesPerSecond"]
        npoints = detdict["nValuesExpected"]
        assert len(detdict["values"]) == npoints, \
            logging.error(f"fusion: Inconsistent trace length in file {fn}.")
        xs = np.linspace(0, npoints/xmul, num=npoints)
        xtol = 0.5 * 1/xmul
        trace["x"] = [[x, xtol, "s"] for x in xs]
        trace["y"] = [[float(y), 1.0, "-"] for y in detdict["values"]]
        chrom["traces"].append(trace)
    return [chrom], metadata, common
    

