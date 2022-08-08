import pytest
import os
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
)

def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    if testspec["method"] is not None:
        assert step["metadata"]["params"]["method"].endswith(testspec["method"])
    tstep = step["data"][testspec["point"]]
    for i in {"height", "area", "concentration", "xout"}:
        for k, v in testspec[i].items():
            compare_result_dicts(tstep["raw"][i][k], v)
    assert tstep["uts"] == testspec["uts"]

@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - fusion-json
                "folders": ["."],
                "prefix": "15p",
                "suffix": "fusion-data",
                "parameters": {
                    "filetype": "fusion.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "method": "AS_Cal_20220204",
                "point": 1,
                "height": {"MeOH": {"n": 0.0, "s": 1.0, "u": " "}},
                "area": {"O2": {"n": 1034.53, "s": 0.01, "u": " "}},
                "concentration": {
                    "CO": {"n": 0.02911539, "s": 0.0000291, "u": "%"}
                },
                "xout": {
                    "C2H6": {"n": 0.22425762, "s": 0.00022426, "u": "%"}
                },
                "uts": 1654697826.467
                
            },
        ),
        (
            {  # ts1 - fusion-zip
                "folders": ["."],
                "prefix": "20220608",
                "suffix": "zip",
                "parameters": {
                    "filetype": "fusion.zip",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 15,
                "method": "AS_Cal_20220204",
                "point": 13,
                "height": {"MeOH": {"n": 0.0, "s": 1.0, "u": " "}},
                "area": {"O2": {"n": 1034.53, "s": 0.01, "u": " "}},
                "concentration": {
                    "CO": {"n": 0.02911539, "s": 0.0000291, "u": "%"}
                },
                "xout": {
                    "C2H6": {"n": 0.22425762, "s": 0.00022426, "u": "%"}
                },
                "uts": 1654697826.467
            },
        ),
        (
            {  # ts1 - fusion-csv
                "folders": ["."],
                "prefix": "20220608",
                "suffix": "csv",
                "parameters": {
                    "filetype": "fusion.csv",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 15,
                "method": "AS_Cal_20220204",
                "point": 1,
                "height": {},
                "area": {"O2": {"n": 1034.53, "s": 0.001, "u": " "}},
                "concentration": {
                    "CO": {"n": 0.02911539, "s": 1e-8, "u": "%"}
                },
                "xout": {
                    "C2H6": {"n": 0.22425762, "s": 1e-8, "u": "%"}
                },
                "uts": 1654697826.0
            },
        ),
    ],
)
def test_datagram_from_chromdata(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromdata", datadir, version="4.2")
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)