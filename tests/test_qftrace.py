import pytest
import os
import json
import numpy as np
from tests.utils import datagram_from_input, standard_datagram_test, datadir


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    tstep = step["data"][testspec["point"]]
    assert (
        len(tstep["raw"]["traces"]["S11"]["f"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["traces"]["S11"]["Re(Γ)"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["traces"]["S11"]["Im(Γ)"]["n"]) == testspec["tracelen"]
    ), "length of 'f', 'Re(Γ)', 'Im(Γ)' not as prescribed."

    assert (
        len(tstep["derived"]["S11"]["Q"]["n"]) == testspec["npeaks"]
    ), "incorrect number of Qs"
    assert (
        len(tstep["derived"]["S11"]["f"]["n"]) == testspec["npeaks"]
    ), "incorrect number of fs"

    Qn = tstep["derived"]["S11"]["Q"]["n"][testspec["peak"]]
    Qs = tstep["derived"]["S11"]["Q"]["s"][testspec["peak"]]
    assert Qn == pytest.approx(testspec["Qn"], abs=1), "wrong Q.n"
    assert Qs == pytest.approx(testspec["Qs"], abs=1), "wrong Q.s"

    fn = tstep["derived"]["S11"]["f"]["n"][testspec["peak"]]
    fs = tstep["derived"]["S11"]["f"]["s"][testspec["peak"]]
    assert fn == pytest.approx(testspec["fn"], abs=10), "wrong f.n"
    assert fs == pytest.approx(testspec["fs"], abs=10), "wrong f.s"

    Q1 = tstep["derived"]["S11"]["Q"]["n"][1]
    Q0 = tstep["derived"]["S11"]["Q"]["n"][0]
    assert 1 / Q1 - 1 / Q0 == pytest.approx(0.00035, abs=0.00005)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - naive with defaults
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {"method": "naive"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "Qn": 2626.506,
                "fn": 7173245000.0,
                "Qs": 1.360,
                "fs": 1000.0,
            },
        ),
        (
            {  # ts1 - naive with a tighter threshold
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {"method": "naive", "threshold": 1e-7},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "Qn": 2567.343,
                "Qs": 1.299,
                "fn": 7173245000.0,
                "fs": 1000.0,
            },
        ),
        (
            {  # ts2 - lorentz with defaults
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {"method": "lorentz"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "Qn": 3093.85372,
                "Qs": 243.395,
                "fn": 7173256009.5,
                "fs": 36639.9,
            },
        ),
        (
            {  # ts3 - lorentz with looser threshold
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {"method": "lorentz", "threshold": 1e-5},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "Qn": 3258.95353,
                "Qs": 284.608,
                "fn": 7173255571.3,
                "fs": 35331.2,
            },
        ),
        (
            {  # ts4 - kajfez with defaults
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {"method": "kajfez"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "Qn": 3061.156,
                "Qs": 18.477,
                "fn": 7173122961.9,
                "fs": 1000.0,
            },
        ),
        (
            {  # ts5 - kajfez with a higher cutoff
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {"method": "kajfez", "cutoff": 0.5},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "Qn": 3053.446,
                "fn": 7173126068.8,
                "Qs": 19.137,
                "fs": 1000.0,
            },
        ),
    ],
)
def test_datagram_from_qftrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "qftrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)


def test_compare_raw_values(datadir):
    input = {
        "folders": ["data_3.1.0/01-inert"],
        "parameters": {},
    }
    os.chdir(datadir)
    ret = datagram_from_input(input, "qftrace", datadir)
    with open("yvals.json", "r") as infile:
        ref = json.load(infile)["traces"]
    for k, v in ret["steps"][0]["data"][0]["raw"]["traces"].items():
        for kk in ["f", "Re(Γ)", "Im(Γ)"]:
            for kkk in ["n", "s"]:
                assert np.allclose(ref[k][kk][kkk], v[kk][kkk])