import json
import os

import numpy as np
import pytest

from tests.utils import datadir, datagram_from_input, standard_datagram_test

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
    # pars_datagram_test(ret, ts)


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
def test_compare_raw_values(input, datadir):
    os.chdir(datadir)
    with open("test_traces.json", "r") as infile:
        ref = json.load(infile)["traces"]
    ret = datagram_from_input(input, "masstrace", datadir)
    ret = ret["steps"][0]["data"][0]["raw"]["traces"]
    for key in ret.keys():
        for ax in ["m/z", "y"]:
            for i in ["n", "s"]:
                assert np.allclose(ref[key][ax][i], ret[key][ax][i], equal_nan=True)
