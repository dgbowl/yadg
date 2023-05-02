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
            {  # ts0 - 01-inert
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "test": {
                    "S11": {
                        "i": 0,
                        "f": {"n": 7.1e9, "s": 1e3, "u": "Hz"},
                        "re": {"n": -0.0192804, "s": 1e-8, "u": " "},
                        "im": {"n": 0.9448405, "s": 1e-7, "u": " "},
                    }
                },
            },
        )
    ],
)
def test_datagram_from_qftrace(input, ts, datadir):
    os.chdir(datadir)
    dg = datagram_from_input(input, "qftrace", datadir)
    step = dg["0"]
    standard_datagram_test(step, ts)
    for k, v in {
        "freq": {"n": 7.1e9, "s": 1e3, "u": "Hz"},
        "Re(G)": {"n": -0.0192804, "s": 1e-8, "u": None},
        "Im(G)": {"n": 0.9448405, "s": 1e-7, "u": None},
    }.items():
        ret = dg_get_quantity(step, "S11", col=k, utsrow=0)
        print(f"{ret=}")
        point = {"n": ret["n"][0], "s": ret["s"][0], "u": ret["u"]}
        compare_result_dicts(point, v)


def test_qftrace_compare_raw_values(datadir):
    input = {
        "folders": ["data_3.1.0/01-inert"],
        "parameters": {},
    }
    os.chdir(datadir)
    dg = datagram_from_input(input, "qftrace", datadir)
    step = dg["0"]
    with open("yvals.json", "r") as infile:
        ref = json.load(infile)["traces"]["S11"]
    for k in {"freq", "Re(G)", "Im(G)"}:
        ret = dg_get_quantity(step, "S11", col=k, utsrow=0)
        print(f"{ret=}")
        compare_result_dicts(ret, ref[k])
