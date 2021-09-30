import logging
import dgutils

def process(fn: str, atol: float = 0.0, rtol: float = 0.0, 
            **kwargs: dict) -> tuple[list, dict, dict]:
    """
    EZ-Chrome export parser.

    One chromatogram per file with multiple traces. A header section
    is followed by y-values for each trace. x-values have to be 
    deduced using number of points, frequency, and x-multiplier. Method name
    is available, but detector names are not - they are assigned their numerical
    index in the file.
    """
    with open(fn, "r", encoding="utf8",  errors='ignore') as infile:
        lines = infile.readlines()
    metadata = {
        "type": "gctrace.datasc",
        "gcparams": {}
    }
    common = {}
    chrom = {"fn": str(fn), "traces": [], "detectors": {}}
    _, datefunc = dgutils.infer_timestamp_from([], 
                            spec = {"timestamp": [0, "%m/%d/%Y %H:%M:%S %p"]})
    
    for line in lines:
        for key in ["Version", "Maxchannels", "Method", "User Name"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                metadata["gcparams"][k] = line.split(f"{key}:")[1].strip()
        for key in ["Sample ID", "Data File"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                chrom[k] = line.split(f"{key}:")[1].strip()
        if line.startswith("Acquisition Date and Time:"):
            chrom["uts"] = datefunc(line.split("Time:")[1].strip())
        if line.startswith("Sampling Rate:"):
            assert "Hz" in line, \
                logging.error(f"datasc: Incorrect units for rate in file {fn}: {line}")
            parts = line.split("\t")
            samplerates = [float(each.strip()) for each in parts[1:-1]]
        if line.startswith("Total Data Points:"):
            assert "Pts." in line, \
                logging.error("datasc: Incorrect units for number of points in file "
                              f"{fn}: {line}")
            parts = line.split("\t")
            npoints = [int(each.strip()) for each in parts[1:-1]]
        if line.startswith("X Axis Title:"):
            parts = line.split("\t")
            xunits = [each.strip() for each in parts[1:]]
        if line.startswith("Y Axis Title:"):
            parts = line.split("\t")
            yunits = [each.strip() for each in parts[1:]]
        if line.startswith("X Axis Multiplier:"):
            parts = line.split("\t")
            xmuls = [float(each.strip()) for each in parts[1:]]
        if line.startswith("Y Axis Multiplier:"):
            parts = line.split("\t")
            ymuls = [float(each.strip()) for each in parts[1:]]
        if ":" not in line:
            si = lines.index(line)
            break
    assert len(samplerates) == len(npoints) == len(xunits) == \
           len(yunits) == len(xmuls) == len(ymuls), \
            logging.error(f"datasc: Inconsistent number of traces in {fn}.")
    for ti in range(len(samplerates)):
        assert xunits[ti] == "Minutes", \
            logging.error(f"datasc: X units label of trace {ti} in {fn} "
                          "was not understood.")
        chrom["detectors"][f"{ti}"] = {"id": ti}
        dt = 60
        xs = [i * xmuls[ti] * dt / samplerates[ti] for i in range(npoints[ti])]
        xtol = max(atol, 0.5 * xmuls[ti] * dt / samplerates[ti], rtol * max(xs))
        ys = [float(i.strip()) * ymuls[ti] for i in lines[si:si+npoints[ti]]]
        ytol = max(atol, rtol * max(ys), ymuls[ti])
        chrom["traces"].append({
            "x": [[x, xtol, "s"] for x in xs],
            "y": [[y, ytol, yunits[ti]] for y in ys]
        })
        si += npoints[ti]
    return [chrom], metadata, common

