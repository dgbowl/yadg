import pytest
import os
from utils import datagram_from_input, standard_datagram_test, datadir


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    tstep = step["data"][testspec["point"]]
    assert (
        len(tstep["raw"]["f"]) == testspec["tracelen"]
        and len(tstep["raw"]["Re(Γ)"]) == testspec["tracelen"]
        and len(tstep["raw"]["Im(Γ)"]) == testspec["tracelen"]
        and len(tstep["raw"]["abs(Γ)"]) == testspec["tracelen"]
    ), "length of 'f', 'Re(Γ)', 'Im(Γ)', and 'abs(Γ)' not as prescribed."
    assert tstep["derived"]["npeaks"] == testspec["npeaks"], "incorrect number of peaks"
    assert len(tstep["derived"]["Q"]) == testspec["npeaks"], "incorrect number of Qs"
    assert len(tstep["derived"]["f"]) == testspec["npeaks"], "incorrect number of fs"
    assert tstep["derived"]["Q"][testspec["peak"]][0] == pytest.approx(
        testspec["Q"], abs=1
    ), "wrong Q"
    assert tstep["derived"]["f"][testspec["peak"]][0] == pytest.approx(
        testspec["f"], abs=10
    ), "wrong f"
    assert 1 / tstep["derived"]["Q"][1][0] - 1 / tstep["derived"]["Q"][0][
        0
    ] == pytest.approx(0.00035, abs=0.00005)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts1 - naive with defaults
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
                "Q": 2626.506,
                "f": 7173245000.0,
            },
        ),
        (
            {  # ts2 - naive with a tighter threshold
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
                "Q": 2567.343,
                "f": 7173245000.0,
            },
        ),
        (
            {  # ts3 - lorentz with defaults
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
                "Q": 3093.853,
                "f": 7173256009.5,
            },
        ),
        (
            {  # ts4 - kajfez with defaults
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
                "Q": 3061.156,
                "f": 7173122656.1,
            },
        ),
        (
            {  # ts5 - kajfez with a higher threshold
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
                "Q": 3054.886,
                "f": 7173125153.7,
            },
        ),
    ],
)
def test_datagram_from_qftrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "qftrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)
