import logging
import dgutils

def _process_headers(headers: list, columns: list, timezone: str) -> dict:
    res = {}
    _, datefunc = dgutils.infer_timestamp_from([], 
                            spec = {"timestamp": {"format": "%d %b %Y %H:%M"}},
                            timezone = timezone)
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

def process(fn: str, encoding: str, timezone: str, atol: float = 0.0, rtol: float = 0.0, 
            **kwargs: dict) -> tuple[list, dict, dict]:
    """
    MassHunter Chromtab format.

    Multiple chromatograms per file with multiple traces. Each chromatogram
    starts with a header section, and is followed by each trace, which 
    includes a header line and x,y-data. Method is not available, but sampleid
    and detector names are included.
    """
    with open(fn, "r", encoding = encoding, errors="ignore") as infile:
        lines = infile.readlines()

    metadata = {
        "type": "gctrace.chromtab",
        "gcparams": {"method": "n/a"}
    }
    common = {}
    chroms = []
    chrom = {"fn": str(fn), "traces": [], "detectors": {}}
    trace = {"x": [], "y": []}
    for li in range(len(lines)):
        line = lines[li].strip()
        parts = line.strip().split(",")
        if len(parts) > 2:
            if '"Date Acquired"' in parts:
                if trace != {"x": [], "y": []}:
                    chrom["traces"].append(trace)
                    trace = {"x": [], "y": []}
                if chrom != {"fn": fn, "traces": [], "detectors": {}}:
                    chroms.append(chrom)
                    chrom = {"fn": fn, "traces": [], "detectors": {}}
                headers = [p.replace('"', "") for p in parts]
            else:
                columns = [p.replace('"', "") for p in parts]
                ret = _process_headers(headers, columns, timezone)
                chrom["uts"] = ret.pop("uts")
                metadata["gcparams"].update(ret)
        elif len(parts) == 1:
            if trace != {"x": [], "y": []}:
                chrom["traces"].append(trace)
                trace = {"x": [], "y": []}
            chrom["detectors"][parts[0].replace('"', "")] = {"id": len(chrom["traces"])}
        elif len(parts) == 2:
            x, y = [float(i) for i in parts]
            tolx = max(0.5 * 10**(-len(parts[0].split(".")[1].strip())), atol, rtol * x)
            toly = max(atol, rtol * abs(y))
            trace["x"].append([x * 60, tolx * 60, "s"])
            trace["y"].append([y, toly, "-"])
    chrom["traces"].append(trace)
    chroms.append(chrom)
    return chroms, metadata, common
    

