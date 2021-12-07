"""
File parser for Fusion json data format (json).

This is a fairly detailed data format, including the traces, the calibration applied,
and also the integrated peak areas. If the peak areas are present, this is returned
in the list of timesteps as a ``"peaks"`` entry.

.. note ::
    The detectors in the trace data are not necessarily in a consistent order, which
    may change between different files. Hence, the keys are sorted.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      sampleid: !!str
      username: None
      version:  !!str
      valve:    !!int
      datafile: !!str

.. codeauthor:: Peter Kraus
"""
import json
import numpy as np

import yadg.dgutils


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
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
    ([chrom], metadata): tuple[list, dict]
        Standard timesteps & metadata tuple.
    """

    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)
    metadata = {
        "filetype": "fusion.json",
        "params": {
            "method": jsdata.get("methodName", "n/a"),
            "sampleid": jsdata.get("annotations", {}).get("name", None),
            "valve": jsdata.get("annotations", {}).get("valcoPosition", None),
            "version": jsdata.get("softwareVersion", {}).get("version", None),
            "datafile": jsdata.get("sequence", {}).get("location", None),
            "username": None,
        },
    }
    chrom = {"fn": str(fn), "traces": {}}
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"timestamp": {}}, timezone=timezone
    )
    chrom["uts"] = datefunc(jsdata["runTimeStamp"])
    detid = 0

    # sort detector keys to ensure alphabetic order for ID matching
    for detname in sorted(jsdata["detectors"].keys()):
        detdict = jsdata["detectors"][detname]
        trace = {"id": detid}
        detid += 1
        xmul = detdict["nValuesPerSecond"]
        npoints = detdict["nValuesExpected"]
        assert (
            len(detdict["values"]) == npoints
        ), f"fusion: Inconsistent trace length in file {fn}."
        xsn = np.arange(npoints) / xmul
        xss = np.ones(npoints) / xmul
        xs = [xsn, xss]
        ysn = np.array(detdict["values"])
        yss = np.ones(npoints)
        ys = [ysn, yss]
        trace["t"] = {
            "n": xsn.tolist(),
            "s": xss.tolist(),
            "u": "s",
        }
        trace["y"] = {
            "n": ysn.tolist(),
            "s": yss.tolist(),
            "u": "-",
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

    return [chrom], metadata
