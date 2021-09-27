from helpers import dateutils
import logging

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
    MassHunter Chromtab format.

    Multiple chromatograms per file with multiple traces. Each chromatogram
    starts with a header section, and is followed by each trace, which 
    includes a header line and x,y-data.
    """
    with open(fn, "r", encoding="utf8", errors="ignore") as infile:
        lines = infile.readlines()

    metadata = {
        "type": "gctrace.chromtab",
        "gcparams": {"method": "n/a"}
    }
    common = {}
    chroms = []
    chrom = {"fn": fn, "traces": []}
    trace = {"x": [], "y": []}
    for li in range(len(lines)):
        line = lines[li].strip()
        parts = line.strip().split(",")
        if len(parts) > 2:
            if '"Date Acquired"' in parts:
                if trace != {"x": [], "y": []}:
                    chrom["traces"].append(trace)
                    trace = {"x": [], "y": []}
                if chrom != {"fn": fn, "traces": []}:
                    chroms.append(chrom)
                    chrom = {"fn": fn, "traces": []}
                headers = [p.replace('"', "") for p in parts]
            else:
                columns = [p.replace('"', "") for p in parts]
                ret = _process_headers(headers, columns)
                chrom["uts"] = ret.pop("uts")
                metadata["gcparams"].update(ret)
        elif len(parts) == 1:
            if trace != {"x": [], "y": []}:
                chrom["traces"].append(trace)
                trace = {"x": [], "y": []}
        elif len(parts) == 2:
            x, y = [float(i) for i in parts]
            tolx = 0.5 * 10**(-len(parts[0].split(".")[1].strip()))
            toly = 1.0
            trace["x"].append([x * 60, tolx * 60, "s"])
            trace["y"].append([y, toly, "-"])
    chrom["traces"].append(trace)
    chroms.append(chrom)
    return chroms, metadata, common
    

