import pytest
import os
import pickle
import numpy as np
import uncertainties as uc
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
    #standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input, ts",
    [
        #(
        #    {  # ts0 - fusion zip file, no smoothing
        #        "folders": ["."],
        #        "prefix": "",
        #        "suffix": "zip",
        #        "parameters": {
        #            "tracetype": "fusion.zip",
        #            "calfile": "calibrations/2022-02-04-GCcal.json",
        #            "detectors": {
        #                "TCD1": {
        #                    "id": 0,
        #                    "peakdetect": {"prominence": 10.0, "threshold": 10.0}
        #                },
        #                "TCD2": {
        #                    "id": 1,
        #                    "peakdetect": {"prominence": 10.0, "threshold": 10.0}
        #                }
        #            }
        #        },
        #    },
        #    {
        #        "nsteps": 1,
        #        "step": 0,
        #        "nrows": 12,
        #        "method": "AS_Cal_20220204",
        #        "point": 4,
        #        "xout": {
        #            "H2":  {"n": 0.6333887, "s": 0.0493695, "u": " "},
        #            "CH4": {"n": 0.0557875, "s": 0.0044479, "u": " "},
        #            "CO":  {"n": 0.0000000, "s": 0.0373813, "u": " "},
        #        },
        #    },
        #),
        (
            {  # ts1 - fusion zip file, minimal smoothing
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
                                "threshold": 10.0
                            }
                        },
                        "TCD2": {
                            "id": 1,
                            "peakdetect": {"prominence": 10.0, "threshold": 10.0}
                        }
                    }
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "xout": {
                    "H2":  {"n": 0.6230303, "s": 0.0437848, "u": " "},
                    "CH4": {"n": 0.0579773, "s": 0.0041758, "u": " "},
                    "CO":  {"n": 0.0136871, "s": 0.0203378, "u": " "},
                },
            },
        ),
        #(
        #    {  # ts2 - fusion zip file, default smoothing
        #        "folders": ["."],
        #        "prefix": "",
        #        "suffix": "zip",
        #        "parameters": {
        #            "tracetype": "fusion.zip",
        #            "calfile": "calibrations/2022-02-04-GCcal.json",
        #            "detectors": {
        #                "TCD1": {
        #                    "id": 0,
        #                    "peakdetect": {
        #                        "window": 7,
        #                        "polyorder": 3,
        #                        "prominence": 10.0,
        #                        "threshold": 10.0
        #                    }
        #                }
        #            }
        #        },
        #    },
        #    {
        #        "nsteps": 1,
        #        "step": 0,
        #        "nrows": 12,
        #        "method": "AS_Cal_20220204",
        #        "point": 4,
        #        "xout": {
        #            "H2":  {"n": 0.6224006, "s": 0.0130895, "u": " "},
        #            "CH4": {"n": 0.0581437, "s": 0.0015272, "u": " "},
        #            "CO":  {"n": 0.0136409, "s": 0.0202494, "u": " "},
        #        },
        #    },
        #),
    ],
)
def test_integration(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromtrace", datadir)
    #standard_datagram_test(ret, ts)
    pmax = ret["steps"][0]["data"][4]["derived"]["pmax"][0]
    pspec = ret["steps"][0]["data"][4]["derived"]["pspec"][0]
    pgrad = ret["steps"][0]["data"][4]["derived"]["pgrad"][0]
    pints = ret["steps"][0]["data"][4]["derived"]["pints"][0]
    pc = ret["steps"][0]["data"][4]["derived"]["concentration"]
    pnorm = ret["steps"][0]["data"][4]["derived"]["norm"]
    # with open(r"C:\Users\krpe\yadg\tests\test_gctrace\pnorm.pkl", "wb") as ouf:
    #     pickle.dump(pnorm, ouf)
    # with open(r"C:\Users\krpe\yadg\tests\test_gctrace\pc.pkl", "wb") as ouf:
    #     pickle.dump(pc, ouf)
    # with open(r"C:\Users\krpe\yadg\tests\test_gctrace\pgrad.pkl", "wb") as ouf:
    #     pickle.dump(pgrad, ouf)
    # with open(r"C:\Users\krpe\yadg\tests\test_gctrace\pints.pkl", "wb") as ouf:
    #     pickle.dump(pints, ouf)
    # with open(r"C:\Users\krpe\yadg\tests\test_gctrace\pmax.pkl", "wb") as ouf:
    #     pickle.dump(pmax, ouf)
    # with open(r"C:\Users\krpe\yadg\tests\test_gctrace\pspec.pkl", "wb") as ouf:
    #     pickle.dump(pspec, ouf)
    with open(r"pmax.pkl", "rb") as inf:
        rmax = pickle.load(inf)
    for k in pmax.keys():
        print(k)
        assert np.allclose(rmax[k], pmax[k])
    with open(r"pspec.pkl", "rb") as inf:
        rspec = pickle.load(inf)
    for i in range(len(pspec)):
        for k in {"llim", "rlim", "max"}:
            print(i, k, rspec[i][k], pspec[i][k])
            assert rspec[i][k] == pspec[i][k]
    with open(r"pgrad.pkl", "rb") as inf:
        rgrad = pickle.load(inf)
    for i in range(len(pgrad)):
        assert np.allclose(pgrad[i], rgrad[i])
    with open(r"pints.pkl", "rb") as inf:
        rints = pickle.load(inf)
    for k in pints.keys():
        for kk in {"llim", "rlim", "max"}:
            print(k, kk, pints[k][kk], rints[k][kk])
            assert pints[k][kk] == rints[k][kk]
        for kk in {"A", "h"}:
            print(k, kk, pints[k][kk], rints[k][kk])
            assert pints[k][kk].n == pytest.approx(rints[k][kk].n, abs=1e-6)
            assert pints[k][kk].s == pytest.approx(rints[k][kk].s, abs=1e-6)
    print(ret["steps"][0]["data"][4]["derived"]["norm"])
    with open(r"pnorm.pkl", "rb") as inf:
        rnorm = pickle.load(inf)
    assert pnorm.n == pytest.approx(rnorm.n, abs=1e-6)
    assert pnorm.s == pytest.approx(rnorm.s, abs=1e-6)
    with open(r"pc.pkl", "rb") as inf:
        rc = pickle.load(inf)
    keys = {"H2", "CH4", "CO"}
    for k in keys:
        print(k, pc[k], rc[k])
        assert pc[k]["n"] == pytest.approx(rc[k]["n"], abs=1e-6)
        assert pc[k]["s"] == pytest.approx(rc[k]["s"], abs=1e-6)
    for k, v in pc.items():
        ck = uc.ufloat(v["n"], v["s"])
        xref1 = ck / pnorm
        xref2 = ck / rnorm
        cr = uc.ufloat(rc[k]["n"], rc[k]["s"])
        xref3 = cr / pnorm
        xref4 = cr / rnorm
        print(k, xref1, xref2, xref3, xref4)
        assert xref1.n == pytest.approx(xref2.n, abs=1e-6)
        assert xref1.n == pytest.approx(xref3.n, abs=1e-6)
        assert xref1.n == pytest.approx(xref4.n, abs=1e-6)
        assert xref1.s == pytest.approx(xref2.s, abs=1e-6)
        assert xref1.s == pytest.approx(xref3.s, abs=1e-6)
        assert xref1.s == pytest.approx(xref4.s, abs=1e-6)
    special_datagram_test(ret, ts)
    