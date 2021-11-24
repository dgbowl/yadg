import numpy as np
import uncertainties.unumpy as unp
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

import yadg.dgutils


def _process_headers(headers: list, columns: list, timezone: str) -> dict:
    res = {}
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"timestamp": {"format": "%d %b %Y %H:%M"}}, timezone=timezone
    )
    assert len(headers) == len(
        columns
    ), f"chromtab: The number of headers and columns do not match."
    assert "Date Acquired" in headers, "chromtab: Cannot infer date."
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


def _to_trace(tx, ty):
    xsn, xss = [np.array(x) * 60 for x in zip(*tx)]
    xs = [xsn, xss]
    ysn, yss = [np.array(y) for y in zip(*ty)]
    ys = [ysn, yss]
    trace = {
        "x": {"n": xsn.tolist(), "s": xss.tolist(), "u": "s"},
        "y": {"n": ysn.tolist(), "s": yss.tolist(), "u": "-"},
        "data": [xs, ys],
    }
    return trace


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    MassHunter Chromtab format.

    Multiple chromatograms per file with multiple traces. Each chromatogram starts with
    a header section, and is followed by each trace, which includes a header line and
    x,y-data. Method is not available, but sampleid and detector names are included.
    """
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()

    metadata = {"type": "gctrace.chromtab", "gcparams": {"method": "n/a"}}
    common = {}
    chroms = []
    chrom = {"fn": str(fn), "traces": {}}
    tx = []
    ty = []
    for li in range(len(lines)):
        line = lines[li].strip()
        parts = line.strip().split(",")
        if len(parts) > 2:
            if '"Date Acquired"' in parts:
                if tx != [] and ty != []:
                    trace = _to_trace(tx, ty)
                    trace["id"] = len(chrom["traces"])
                    chrom["traces"][detname] = trace
                    tx = []
                    ty = []
                if chrom != {"fn": fn, "traces": {}}:
                    chroms.append(chrom)
                    chrom = {"fn": fn, "traces": {}}
                headers = [p.replace('"', "") for p in parts]
            else:
                columns = [p.replace('"', "") for p in parts]
                ret = _process_headers(headers, columns, timezone)
                chrom["uts"] = ret.pop("uts")
                metadata["gcparams"].update(ret)
        elif len(parts) == 1:
            if tx != [] and ty != []:
                trace = _to_trace(tx, ty)
                trace["id"] = len(chrom["traces"])
                chrom["traces"][detname] = trace
                tx = []
                ty = []
            detname = parts[0].replace('"', "").split("\\")[-1]
        elif len(parts) == 2:
            x, y = [tuple_fromstr(i) for i in parts]
            tx.append(x)
            ty.append(y)
    trace = _to_trace(tx, ty)
    trace["id"] = len(chrom["traces"])
    chrom["traces"][detname] = trace
    chroms.append(chrom)
    return chroms, metadata, common
