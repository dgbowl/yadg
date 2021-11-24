import pytest
import os
from tests.schemas import gctrace_chromtab
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    datadir,
    compare_result_dicts,
)
import numpy as np


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    assert step["metadata"]["lcparams"]["method"].endswith(testspec["method"])
    tstep = step["data"][testspec["point"]]
    for k, v in testspec["peaks"].items():
        compare_result_dicts(tstep["derived"]["peaks"]["LC"][k]["A"], v)


refvals = {
    "a": {"n": 4250.5393537, "s": 3.1582251, "u": "-"},
    "b": {"n": 23454.1192411, "s": 16.2072645, "u": "-"},
    "c": {"n": 71369.5831322, "s": 44.2360720, "u": "-"},
    "d": {"n": 13175.0417324, "s": 7.2314229, "u": "-"},
}


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - ch file parse, method, and integration
                "folders": ["."],
                "suffix": "CH",
                "parameters": {"tracetype": "ch", "calfile": "lc_calfile.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "method": "CO2RR_FTI_0.7mL_40uL_45dgr_36min.amx",
                "point": 0,
                "peaks": refvals,
            },
        ),
        (
            {  # ts1 - dx file unzip, parse, method, integration from file
                "folders": ["."],
                "suffix": "dx",
                "parameters": {"tracetype": "dx", "calfile": "lc_calfile.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "method": "CO2RR_FTI_0.7mL_40uL_45dgr_36min.amx",
                "point": 0,
                "peaks": refvals,
            },
        ),
    ],
)
def test_datagram_from_lctrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "lctrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)
