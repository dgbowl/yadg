import logging
from uncertainties import ufloat_fromstr, unumpy
import numpy as np

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


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    MassHunter Chromtab format.

    Multiple chromatograms per file with multiple traces. Each chromatogram starts with a header section, and is followed by each trace, which includes a header line and x,y-data. Method is not available, but sampleid and detector names are included.
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
                if tx  != [] and ty != []:
                    tx = np.array(tx)
                    ty = np.array(ty)
                    trace = {
                        "x": {"n": list(unumpy.nominal_values(tx)), "s": list(unumpy.std_devs(tx)), "u": "s"},
                        "y": {"n": list(unumpy.nominal_values(ty)), "s": list(unumpy.std_devs(ty)), "u": "-"},
                        "id": len(chrom["traces"]),
                        "data": [tx, ty]
                    }
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
            if tx  != [] and ty != []:
                tx = np.array(tx)
                ty = np.array(ty)
                trace = {
                    "x": {"n": list(unumpy.nominal_values(tx)), "s": list(unumpy.std_devs(tx)), "u": "s"},
                    "y": {"n": list(unumpy.nominal_values(ty)), "s": list(unumpy.std_devs(ty)), "u": "-"},
                    "id": len(chrom["traces"]),
                    "data": [tx, ty]
                }
                chrom["traces"][detname] = trace
                tx = []
                ty = []
            detname = parts[0].replace('"', "").split("\\")[-1]
        elif len(parts) == 2:
            x, y = [ufloat_fromstr(i) for i in parts]
            tx.append(x*60)
            ty.append(y)
    tx = np.array(tx)
    ty = np.array(ty)
    trace = {
        "x": {"n": list(unumpy.nominal_values(tx)), "s": list(unumpy.std_devs(tx)), "u": "s"},
        "y": {"n": list(unumpy.nominal_values(ty)), "s": list(unumpy.std_devs(ty)), "u": "-"},
        "id": len(chrom["traces"]),
        "data": [tx, ty]
    }
    chrom["traces"][detname] = trace
    chroms.append(chrom)
    return chroms, metadata, common
