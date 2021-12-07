"""
File parser for EZ-Chrom ASCII export files (dat.asc).

This file format includes one timestep with multiple traces in each ASCII file. It 
contains a header section, and a sequence of Y datapoints for each detector. The X
axis is uniform between traces, and its units have to be deduced from the header.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      sampleid: !!str
      username: !!str
      version:  !!str
      valve:    None
      datafile: !!str

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""
import numpy as np
import uncertainties as uc
import uncertainties.unumpy as unp
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

import yadg.dgutils


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    EZ-Chrome ASCII export file parser.

    One chromatogram per file with multiple traces. A header section is followed by
    y-values for each trace. x-values have to be deduced using number of points,
    frequency, and x-multiplier. Method name is available, but detector names are not.
    They are assigned their numerical index in the file.

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
        lines = infile.readlines()
    metadata = {"filetype": "ezchrom.datasc", "params": {"valve": None}}
    chrom = {"fn": str(fn), "traces": {}}

    _, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"timestamp": {"format": "%m/%d/%Y %I:%M:%S %p"}}, timezone=timezone
    )
    for line in lines:
        for key in ["Version", "Method", "User Name"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                metadata["params"][k] = line.split(f"{key}:")[1].strip()
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
        xsn = np.arange(npoints[ti]) * xmul
        xss = np.ones(npoints[ti]) * xmul
        xs = [xsn, xss]
        ytup = [tuple_fromstr(l) for l in lines[si : si + npoints[ti]]]
        ysn, yss = [np.array(p) * ymul for p in zip(*ytup)]
        ys = [ysn, yss]
        chrom["traces"][f"{ti}"] = {"id": ti, "data": [xs, ys]}
        chrom["traces"][f"{ti}"]["t"] = {
            "n": xsn.tolist(),
            "s": xss.tolist(),
            "u": "s",
        }
        chrom["traces"][f"{ti}"]["y"] = {
            "n": ysn.tolist(),
            "s": yss.tolist(),
            "u": yunits[ti],
        }

        si += npoints[ti]
    return [chrom], metadata
