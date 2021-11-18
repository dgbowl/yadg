import pytest
import os
from tests.schemas import gctrace_chromtab
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    datadir,
    compare_result_dicts,
)


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    assert step["metadata"]["gcparams"]["method"].endswith(testspec["method"])
    tstep = step["data"][testspec["point"]]
    for k, v in testspec["xout"].items():
        compare_result_dicts(tstep["derived"]["xout"][k], v)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts1 - datasc parse & integration from file
                "folders": ["."],
                "prefix": "2019-12-03",
                "suffix": "dat.asc",
                "parameters": {"tracetype": "datasc", "calfile": "gc_5890_FHI.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "polyarc+TCD_PK_09b.met",
                "point": 1,
                "xout": {
                    "O2": {"n": 0.0460576, "s": 0.0009251, "u": "-"},
                    "propane": {"n": 0.0232967, "s": 0.0003698, "u": "-"},
                    "N2": {"n": 0.9177570, "s": 0.0009767, "u": "-"},
                },
            },
        ),
        (
            {  # ts1 - datasc parse & integration from file
                "folders": ["."],
                "prefix": "2019-12-03",
                "suffix": "dat.asc",
                "parameters": {"tracetype": "datasc", "calfile": "gc_5890_FHI.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "polyarc+TCD_PK_09b.met",
                "point": 4,
                "xout": {
                    "O2": {"n": 0.0362046, "s": 0.0007409, "u": "-"},
                    "propane": {"n": 0.0219253, "s": 0.0003478, "u": "-"},
                    "N2": {"n": 0.9157070, "s": 0.0008484, "u": "-"},
                },
            },
        ),
        (
            {  # ts2 - chromtab parse & integration from file
                "folders": ["."],
                "prefix": "CHROMTAB",
                "suffix": "CSV",
                "parameters": {"tracetype": "chromtab", "calfile": "gc_chromtab.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "method": "n/a",
                "point": 2,
                "xout": {
                    "N2": {"n": 0.6746582, "s": 0.0017331, "u": "-"},
                    "CH3OH": {"n": 0.3205363, "s": 0.0017346, "u": "-"},
                },
            },
        ),
        (
            {  # ts3 - datasc parse & integration from species & detector
                "folders": ["."],
                "prefix": "CHROMTAB",
                "suffix": "CSV",
                "parameters": {
                    "tracetype": "chromtab",
                    "species": gctrace_chromtab["sp"],
                    "detectors": gctrace_chromtab["det"],
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "method": "n/a",
                "point": 0,
                "xout": {
                    "N2": {"n": 0.6474110, "s": 0.0018352, "u": "-"},
                    "CH3OH": {"n": 0.3429352, "s": 0.0018353, "u": "-"},
                },
            },
        ),
        (
            {  # ts4 - fusion parse & integration from file
                "folders": ["."],
                "prefix": "",
                "suffix": "fusion-data",
                "parameters": {"tracetype": "fusion", "calfile": "gc_fusion.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "AS_Cal_20210702",
                "point": 0,
                "xout": {
                    "H2": {"n": 0.9942275, "s": 0.0000306, "u": "-"},
                    "CO": {"n": 0.0057725, "s": 0.0000298, "u": "-"},
                },
            },
        ),
        (
            {  # ts5 - fusion parse & integration from file
                "folders": ["."],
                "prefix": "",
                "suffix": "fusion-data",
                "parameters": {"tracetype": "fusion", "calfile": "gc_fusion.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "AS_Cal_20210702",
                "point": 4,
                "xout": {
                    "H2": {"n": 0.0289302, "s": 0.0001283, "u": "-"},
                    "CO2": {"n": 0.9710112, "s": 0.0001283, "u": "-"},
                },
            },
        ),
    ],
)
def test_datagram_from_gctrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "gctrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)
