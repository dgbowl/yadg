import logging
import numpy as np
from uncertainties import ufloat_fromstr, ufloat, unumpy

import yadg.dgutils


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    EZ-Chrome export parser.

    One chromatogram per file with multiple traces. A header section is followed by y-values for each trace. x-values have to be deduced using number of points, frequency, and x-multiplier. Method name is available, but detector names are not - they are assigned their numerical index in the file.
    """
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()
    metadata = {"type": "gctrace.datasc", "gcparams": {}}
    common = {}
    chrom = {"fn": str(fn), "traces": {}}
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"timestamp": {"format": "%m/%d/%Y %I:%M:%S %p"}}, timezone=timezone
    )

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
            assert (
                "Hz" in line
            ), f"datasc: Incorrect units for rate in file {fn}: {line}"
            parts = line.split("\t")
            samplerates = [float(each.strip()) for each in parts[1:-1]]
        if line.startswith("Total Data Points:"):
            assert (
                "Pts." in line
            ), f"datasc: Incorrect units for number of points in file {fn}: {line}"
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
    assert (
        len(samplerates)
        == len(npoints)
        == len(xunits)
        == len(yunits)
        == len(xmuls)
        == len(ymuls)
    ), f"datasc: Inconsistent number of traces in {fn}."
    for ti in range(len(samplerates)):
        assert (
            xunits[ti] == "Minutes"
        ), f"datasc: X units label of trace {ti} in {fn} was not understood."
        dt = 60
        xmul = xmuls[ti] * dt / samplerates[ti]
        ymul = ymuls[ti]
        xs = unumpy.uarray(np.arange(npoints[ti]), np.ones(npoints[ti]) * 0.5) * xmul
        ys = np.array([ufloat_fromstr(i.strip()) for i in lines[si : si + npoints[ti]]]) * ymul
        chrom["traces"][f"{ti}"] = {
            "x": {
                "n": list(unumpy.nominal_values(xs)), 
                "s": list(unumpy.std_devs(xs)), 
                "u": "s"
            },
            "y": {
                "n": list(unumpy.nominal_values(ys)),
                "s": list(unumpy.std_devs(ys)),
                "u": yunits[ti]
            },
            "id": ti,
            "data": [xs, ys]
        }
        si += npoints[ti]
    return [chrom], metadata, common
