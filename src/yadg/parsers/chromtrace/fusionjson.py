"""
**fusionjson**: Processing Inficon Fusion json data format (json).
------------------------------------------------------------------

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
      datafile: !!str

.. codeauthor:: Peter Kraus
"""
import json
import numpy as np
from ...dgutils.dateutils import str_to_uts


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
    """
    Fusion json format.

    One chromatogram per file with multiple traces, and integrated peak areas.

    .. warning::

        To parse the integrated data present in these files, use the
        :mod:`~yadg.parsers.chromdata` parser.

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
            "version": jsdata.get("softwareVersion", {}).get("version", None),
            "datafile": jsdata.get("sequence", {}).get("location", None),
            "username": None,
        },
    }
    chrom = {"fn": str(fn), "traces": {}, "raw": {}}
    chrom["uts"] = str_to_uts(jsdata["runTimeStamp"], timezone=timezone)
    detid = 0

    valve = jsdata.get("annotations", {}).get("valcoPosition", None)
    if valve is not None:
        chrom["raw"]["valve"] = valve

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
            "u": " ",
        }
        trace["data"] = [xs, ys]
        chrom["traces"][detname] = trace

    return [chrom], metadata
