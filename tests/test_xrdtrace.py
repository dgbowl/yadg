import json
import os

import numpy as np
import pytest

from .utils import datagram_from_input, standard_datagram_test, compare_result_dicts

# Tests for the xrdtrace parser:


@pytest.mark.parametrize(
    "input, ts",
    [
        (  # ts0 - xy data
            {"case": "210520step1_30min.xy", "parameters": {"tracetype": "panalytical.xy"}},
            {"nsteps": 1, "step": 0, "nrows": 1},
        ),
        (  # ts1 - csv data
            {"case": "210520step1_30min.csv", "parameters": {"tracetype": "panalytical.csv"}},
            {"nsteps": 1, "step": 0, "nrows": 1},
        ),
        #(  # ts3 - 
        #    {"case": "210520step1_30min.xrdml", "parameters": {"tracetype": "panalytical.xrdml"}},
        #    {"nsteps": 1, "step": 0, "nrows": 0, "point": 0,},
        #),
    ],
)
def test_datagram_from_xrdtrace(input, ts, datadir):
    ret = datagram_from_input(input, "xrdtrace", datadir)
    print(ret["steps"][0]["data"][0].keys())
    standard_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input, refpath",
    [
        (
            {  # ts0 - test.sac
                "case": "test.sac",
                "parameters": {"tracetype": "quadstar.sac"},
            },
            "xrd_data.json",
        ),
        (
            {  # ts0 - test.sac
                "case": "test.sac",
                "parameters": {"tracetype": "quadstar.sac"},
            },
            "xrd_data.json",
        ),
        (
            {  # ts0 - test.sac
                "case": "test.sac",
                "parameters": {"tracetype": "quadstar.sac"},
            },
            "xrd_data.json",
        ),
    ],
)


# TODO


def test_compare_raw_values(input, refpath, datadir):
    assert True
#    os.chdir(datadir)
#    with open(refpath, "r") as infile:
#        ref = json.load(infile)["traces"]
#    ret = datagram_from_input(input, "masstrace", datadir)
#    ret = ret["steps"][0]["data"][0]["raw"]["traces"]
#    for key in ret.keys():
#        for ax in ["m/z", "y"]:
#            for i in ["n", "s"]:
#                assert np.allclose(ref[key][ax][i], ret[key][ax][i], equal_nan=True)
