import json
import os
import pytest

from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
    dg_get_quantity,
)


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
        (  # ts2 - check concatenation
            {
                "files": ["test0.spe", "test0b.spe"],
                "parameters": {"tracetype": "phi.spe"},
            },
            {"nsteps": 1, "step": 0, "nrows": 2, "point": 0},
        ),
    ],
)
def test_datagram_from_xpstrace(input, ts, datadir):
    ret = datagram_from_input(input, "xpstrace", datadir)
    print(f"{ret=}")
    standard_datagram_test(ret, ts)


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
def test_xpstrace_compare_raw_values(input, datadir):
    os.chdir(datadir)
    with open("test0.json", "r") as infile:
        ref = json.load(infile)["traces"]
    dg = datagram_from_input(input, "xpstrace", datadir)
    step = dg["0"]
    for k in {"1su", "F1s"}:
        for kk in {"y", "E"}:
            ret = dg_get_quantity(step, k, col=kk, utsrow=0)
            compare_result_dicts(ret, ref[k][kk])
