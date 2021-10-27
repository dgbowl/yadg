import pytest
import os
from schemas import gctrace_chromtab
from utils import datagram_from_input, standard_datagram_test, datadir


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    assert step["metadata"]["gcparams"]["method"].endswith(testspec["method"])
    tstep = step["data"][testspec["point"]]
    for k, v in testspec["xout"].items():
        assert tstep["derived"]["xout"][k][0] == pytest.approx(v, abs=0.001)


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
                "xout": {"O2": 0.046, "propane": 0.023, "N2": 0.918},
            },
        ),
        (
            {  # ts2 - datasc parse & integration from file
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
                "xout": {"O2": 0.036, "propane": 0.022, "N2": 0.915},
            },
        ),
        (
            {  # ts3 - chromtab parse & integration from file
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
                "xout": {"N2": 0.674, "CH3OH": 0.320},
            },
        ),
        (
            {  # ts4 - datasc parse & integration from species & detector
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
                "xout": {"N2": 0.647, "CH3OH": 0.343},
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
                "point": 0,
                "xout": {"H2": 0.994, "CO": 0.006},
            },
        ),
        (
            {  # ts6 - fusion parse & integration from file
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
                "xout": {"H2": 0.029, "CO2": 0.971},
            },
        ),
    ],
)
def test_datagram_from_gctrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "gctrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)
