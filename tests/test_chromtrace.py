import pytest
import os
import json
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
    dg_get_quantity,
)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - datasc parse & integration from file
                "folders": ["."],
                "prefix": "2019-12-03",
                "suffix": "dat.asc",
                "parameters": {"tracetype": "ezchrom.asc"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "polyarc+TCD_PK_09b.met",
                "point": 1,
                "test": {
                    "0": {
                        "i": 1000,
                        "elution_time": {"n": 100.002, "s": 0.100002, "u": "s"},
                        "signal": {"n": 2.085281, "s": 0.000130, "u": "pA"},
                    },
                    "1": {
                        "i": 1000,
                        "elution_time": {"n": 100.002, "s": 0.100002, "u": "s"},
                        "signal": {"n": 55.892435, "s": 0.000130, "u": "V"},
                    },
                },
            },
        ),
        (
            {  # ts2 - fusion json parse
                "folders": ["."],
                "prefix": "",
                "suffix": "fusion-data",
                "parameters": {"tracetype": "fusion.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "AS_Cal_20210702",
                "point": 4,
                "test": {
                    "moduleA:tcd": {
                        "i": 100,
                        "elution_time": {"n": 2.0, "s": 0.02, "u": "s"},
                        "signal": {"n": 1566.0, "s": 1.0, "u": None},
                    },
                    "moduleB:tcd": {
                        "i": 100,
                        "elution_time": {"n": 2.0, "s": 0.02, "u": "s"},
                        "signal": {"n": -1412.0, "s": 1.0},
                    },
                },
            },
        ),
        (
            {  # ts3 - fusion zip parse
                "folders": ["."],
                "prefix": "",
                "suffix": "zip",
                "parameters": {"tracetype": "fusion.zip"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "test": {
                    "moduleA:tcd": {
                        "i": 0,
                        "elution_time": {"n": 0.0, "s": 0.02, "u": "s"},
                        "signal": {"n": 0.0, "s": 1.0, "u": None},
                    }
                },
            },
        ),
    ],
)
def test_datagram_from_chromtrace(input, ts, datadir):
    os.chdir(datadir)
    dg = datagram_from_input(input, "chromtrace", datadir)
    print(f"{dg=}")
    standard_datagram_test(dg, ts)
    if isinstance(ts["step"], str):
        step = dg[ts["step"]]
    else:
        step = dg[list(dg.children.keys())[ts["step"]]]
    for k, v in ts["test"].items():
        for kk in {"signal", "elution_time"}:
            ret = dg_get_quantity(step, k, col=kk, utsrow=ts["point"])
            print(f"{v[kk]=}")
            print(f"{ret=}")
            compare_result_dicts(
                {"n": ret["n"][v["i"]], "s": ret["s"][v["i"]], "u": ret["u"]},
                v[kk],
            )