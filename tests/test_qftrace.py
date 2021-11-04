import pytest
import os
from utils import datagram_from_input, standard_datagram_test, datadir


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    tstep = step["data"][testspec["point"]]
    assert (
        len(tstep["raw"]["f"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["Re(Γ)"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["Im(Γ)"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["abs(Γ)"]["n"]) == testspec["tracelen"]
    ), "length of 'f', 'Re(Γ)', 'Im(Γ)', and 'abs(Γ)' not as prescribed."

    assert (
        len(tstep["derived"]["Q"]["n"]) == testspec["npeaks"]
    ), "incorrect number of Qs"
    assert (
        len(tstep["derived"]["f"]["n"]) == testspec["npeaks"]
    ), "incorrect number of fs"

    Qn = tstep["derived"]["Q"]["n"][testspec["peak"]]
    Qs = tstep["derived"]["Q"]["s"][testspec["peak"]]
    assert Qn == pytest.approx(testspec["Qn"], abs=1), "wrong Q.n"
    assert Qs == pytest.approx(testspec["Qs"], abs=1), "wrong Q.s"

    fn = tstep["derived"]["f"]["n"][testspec["peak"]]
    fs = tstep["derived"]["f"]["s"][testspec["peak"]]
    assert fn == pytest.approx(testspec["fn"], abs=10), "wrong f.n"
    assert fs == pytest.approx(testspec["fs"], abs=10), "wrong f.s"

    Q1 = tstep["derived"]["Q"]["n"][1]
    Q0 = tstep["derived"]["Q"]["n"][0]
    assert 1 / Q1 - 1 / Q0 == pytest.approx(0.00035, abs=0.00005)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - naive with defaults
                "folders": ["."],
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
                "folders": ["."],
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
                "folders": ["."],
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
                "Qn": 2611.599,
                "Qs": 67.399,
                "fn": 7173243292.3,
                "fs": 68479751.0,
            },
        ),
        (
            {  # ts3 - kajfez with defaults
                "folders": ["."],
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
            {  # ts4 - kajfez with a higher cutoff
                "folders": ["."],
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
