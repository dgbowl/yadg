import json
import os

import numpy as np
import pytest

from tests.utils import datadir, datagram_from_input, standard_datagram_test

# TODO: Implement more thorough tests.


@pytest.mark.parametrize(
    "input, ts",
    [
        (  # ts0 - test0.spe
            {"case": "test0.spe", "parameters": {"tracetype": "phi.spe"}},
            {"nsteps": 1, "step": 0, "nrows": 1, "point": 0},
        ),
        (  # ts1 - test1.spe
            {"case": "test1.spe", "parameters": {"tracetype": "phi.spe"}},
            {"nsteps": 1, "step": 0, "nrows": 1, "point": 0},
        ),
    ],
)
def test_datagram_from_quadstar(input, ts, datadir):
    ret = datagram_from_input(input, "xpstrace", datadir)
    standard_datagram_test(ret, ts)
    # pars_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input",
    [
        (
            {  # ts0 - test0.spe
                "case": "test0.spe",
                "parameters": {"tracetype": "phi.spe"},
            }
        ),
    ],
)
def test_compare_raw_values(input, datadir):
    os.chdir(datadir)
    with open("test0.json", "r") as infile:
        ref = json.load(infile)["traces"]
    ret = datagram_from_input(input, "xpstrace", datadir)
    ret = ret["steps"][0]["data"][0]["raw"]["traces"]
    for key in ret.keys():
        for ax in ["E", "y"]:
            for i in ["n", "s"]:
                assert np.allclose(ref[key][ax][i], ret[key][ax][i], equal_nan=True)
