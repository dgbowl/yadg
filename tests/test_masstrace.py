import json
import os
import pytest

from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    dg_get_quantity,
    compare_result_dicts,
)

# Tests for the quadstar parser:
# TODO: Implement more thorough tests.


@pytest.mark.parametrize(
    "input, ts",
    [
        (  # ts0 - airdemo.sac
            {"case": "airdemo.sac", "parameters": {"tracetype": "quadstar.sac"}},
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 21,
                "point": 0,
            },
        ),
        (  # ts1 - test.sac
            {"case": "test.sac", "parameters": {"tracetype": "quadstar.sac"}},
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 188,
                "point": 0,
            },
        ),
    ],
)
def test_datagram_from_quadstar(input, ts, datadir):
    ret = datagram_from_input(input, "masstrace", datadir)
    standard_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input",
    [
        (
            {  # ts0 - test.sac
                "case": "test.sac",
                "parameters": {"tracetype": "quadstar.sac"},
            }
        ),
    ],
)
def test_masstrace_compare_raw_values(input, datadir):
    os.chdir(datadir)
    with open("test_traces.json", "r") as infile:
        ref = json.load(infile)["traces"]
    dg = datagram_from_input(input, "masstrace", datadir)
    step = dg["0"]
    for k in ["1", "2"]:
        for kk in ["mass_to_charge", "y"]:
            print(f"{k=}, {kk=}")
            ret = dg_get_quantity(step, k, col=kk, utsrow=0)
            compare_result_dicts(ret, ref[k][kk])
