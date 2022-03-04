import pytest
import os
from tests.schemas import gctrace_chromtab
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
)


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    if testspec["method"] is not None:
        assert step["metadata"]["params"]["method"].endswith(testspec["method"])
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
                "parameters": {
                    "tracetype": "ezchrom.asc",
                    "calfile": "gc_5890_FHI.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "polyarc+TCD_PK_09b.met",
                "point": 1,
                "xout": {
                    "O2": {"n": 0.0460576, "s": 0.0009251, "u": " "},
                    "propane": {"n": 0.0232996, "s": 0.0003698, "u": " "},
                    "N2": {"n": 0.91775537, "s": 0.0009767, "u": " "},
                },
            },
        ),
        (
            {  # ts1 - datasc parse & integration from file
                "folders": ["."],
                "prefix": "2019-12-03",
                "suffix": "dat.asc",
                "parameters": {
                    "tracetype": "ezchrom.asc",
                    "calfile": "gc_5890_FHI.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "polyarc+TCD_PK_09b.met",
                "point": 4,
                "xout": {
                    "O2": {"n": 0.0362035, "s": 0.0007409, "u": " "},
                    "propane": {"n": 0.0219293, "s": 0.0003478, "u": " "},
                    "N2": {"n": 0.9157086, "s": 0.0008484, "u": " "},
                },
            },
        ),
        (
            {  # ts2 - chromtab parse & integration from file
                "folders": ["."],
                "prefix": "CHROMTAB",
                "suffix": "CSV",
                "parameters": {
                    "tracetype": "agilent.csv",
                    "calfile": "gc_chromtab.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "method": None,
                "point": 2,
                "xout": {
                    "N2": {"n": 0.6746582, "s": 0.0017331, "u": " "},
                    "CH3OH": {"n": 0.3205363, "s": 0.0017346, "u": " "},
                },
            },
        ),
        (
            {  # ts3 - datasc parse & integration from species & detector
                "folders": ["."],
                "prefix": "CHROMTAB",
                "suffix": "CSV",
                "parameters": {
                    "tracetype": "agilent.csv",
                    "species": gctrace_chromtab["sp"],
                    "detectors": gctrace_chromtab["det"],
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "method": None,
                "point": 0,
                "xout": {
                    "N2": {"n": 0.6474110, "s": 0.0018352, "u": " "},
                    "CH3OH": {"n": 0.3429352, "s": 0.0018353, "u": " "},
                },
            },
        ),
        (
            {  # ts4 - fusion parse & integration from file
                "folders": ["."],
                "prefix": "",
                "suffix": "fusion-data",
                "parameters": {
                    "tracetype": "fusion.json",
                    "calfile": "gc_fusion.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "AS_Cal_20210702",
                "point": 0,
                "xout": {
                    "H2": {"n": 0.9942164, "s": 0.0000300, "u": " "},
                    "CO": {"n": 0.0057545, "s": 0.0000298, "u": " "},
                },
            },
        ),
        (
            {  # ts5 - fusion parse & integration from file
                "folders": ["."],
                "prefix": "",
                "suffix": "fusion-data",
                "parameters": {
                    "tracetype": "fusion.json",
                    "calfile": "gc_fusion.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "AS_Cal_20210702",
                "point": 4,
                "xout": {
                    "H2": {"n": 0.0289236, "s": 0.0001283, "u": " "},
                    "CO2": {"n": 0.9710181, "s": 0.0001283, "u": " "},
                },
            },
        ),
        (
            {  # ts6 - fusion zip parse & integration from file
                "folders": ["."],
                "prefix": "",
                "suffix": "zip",
                "parameters": {
                    "tracetype": "fusion.zip",
                    "calfile": "calibrations/2022-02-04-GCcal.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "xout": {},
            },
        ),
    ],
)
def test_datagram_from_gctrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromtrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - fusion zip file, no smoothing
                "folders": ["."],
                "prefix": "",
                "suffix": "zip",
                "parameters": {
                    "tracetype": "fusion.zip",
                    "calfile": "calibrations/2022-02-04-GCcal.json",
                    "detectors": {
                        "TCD1": {
                            "id": 0,
                            "peakdetect": {"prominence": 10.0, "threshold": 10.0},
                        },
                        "TCD2": {
                            "id": 1,
                            "peakdetect": {"prominence": 10.0, "threshold": 10.0},
                        },
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "xout": {
                    "H2": {"n": 0.6333887, "s": 0.0493695, "u": " "},
                    "CH4": {"n": 0.0557875, "s": 0.0044479, "u": " "},
                    "CO": {"n": 0.0000000, "s": 0.0373813, "u": " "},
                },
            },
        ),
        (
            {  # ts1 - fusion zip file, minimal smoothing on TCD 1
                "folders": ["."],
                "prefix": "",
                "suffix": "zip",
                "parameters": {
                    "tracetype": "fusion.zip",
                    "calfile": "calibrations/2022-02-04-GCcal.json",
                    "detectors": {
                        "TCD1": {
                            "id": 0,
                            "peakdetect": {
                                "window": 3,
                                "polyorder": 2,
                                "prominence": 10.0,
                                "threshold": 10.0,
                            },
                        },
                        "TCD2": {
                            "id": 1,
                            "peakdetect": {"prominence": 10.0, "threshold": 10.0},
                        },
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "xout": {
                    "H2": {"n": 0.6230303, "s": 0.0437848, "u": " "},
                    "CH4": {"n": 0.0579773, "s": 0.0041758, "u": " "},
                    "CO": {"n": 0.0136871, "s": 0.0203378, "u": " "},
                },
            },
        ),
        (
            {  # ts2 - fusion zip file, default smoothing on TCD1
                "folders": ["."],
                "prefix": "",
                "suffix": "zip",
                "parameters": {
                    "tracetype": "fusion.zip",
                    "calfile": "calibrations/2022-02-04-GCcal.json",
                    "detectors": {
                        "TCD1": {
                            "id": 0,
                            "peakdetect": {
                                "window": 7,
                                "polyorder": 3,
                                "prominence": 10.0,
                                "threshold": 10.0,
                            },
                        },
                        "TCD2": {
                            "id": 1,
                            "peakdetect": {"prominence": 10.0, "threshold": 10.0},
                        },
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "xout": {
                    "H2": {"n": 0.6233586, "s": 0.0437275, "u": " "},
                    "CH4": {"n": 0.0582332, "s": 0.0041865, "u": " "},
                    "CO": {"n": 0.0136619, "s": 0.0203008, "u": " "},
                },
            },
        ),
    ],
)
def test_integration(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromtrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)
