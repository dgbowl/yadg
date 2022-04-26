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
            {"nsteps": 1, "step": 0, "nrows": 1, "point": 0},
        ),
        (  # ts1 - csv data
            {"case": "210520step1_30min.csv", "parameters": {"tracetype": "panalytical.csv"}},
            {"nsteps": 1, "step": 0, "nrows": 1, "point": 0},
        ),
        (  # ts2 - xml data 
            {"case": "210520step1_30min.xrdml", "parameters": {"tracetype": "panalytical.xrdml"}},
            {"nsteps": 1, "step": 0, "nrows": 1, "point": 0},
        ),
    ],
)
def test_datagram_from_xrdtrace(input, ts, datadir):
    dg = datagram_from_input(input, "xrdtrace", datadir)
    standard_datagram_test(dg, ts)
    with open("xrd_data.json", "r") as inf:
        ref = json.load(inf)
    for k in {"intensity", "angle"}:
        ret = dg["steps"][ts["step"]]["data"][ts["point"]]["raw"]["traces"]["0"][k]
        compare_result_dicts(ret, ref[k])
    
