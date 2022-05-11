import pytest
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    pars_datagram_test,
)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - plain time, float offset
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {"from": {"utsoffset": 0.0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {
                    "flow": {"sigma": 0.1, "value": 15.0, "unit": "ml/min"},
                    "uts": {"value": 43140.0},
                },
            },
        ),
        (
            {  # ts1 - plain time, string offset
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {"from": {"isostring": "2021-01-01"}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {"uts": {"value": 1609502340.0}},
            },
        ),
        (
            {  # ts2 - plain time, json file, iso string, implied partial
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {
                    "from": {"file": {"path": "file_2.json", "type": "json"}}
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {"uts": {"value": 1262347140.0}},
            },
        ),
        (
            {  # ts3 - plain time, json file, iso string, full replace
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {
                    "from": {"file": {"path": "file_3.json", "type": "json"}},
                    "mode": "replace",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {"uts": {"value": 1262433540.0}},
            },
        ),
        (
            {  # ts4 - plain time, pickle file, string, full replace
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {
                    "from": {"file": {"path": "file_4.pkl", "type": "pkl"}},
                    "mode": "replace",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {"uts": {"value": 1641810718.0}},
            },
        ),
        (
            {  # ts5 - plain time, pickle file, np.ones(3), partial
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {
                    "from": {"file": {"path": "file_5.pkl", "type": "pkl"}},
                    "mode": "add",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {"uts": {"value": 43141.0}},
            },
        ),
        (
            {  # ts6 -
                "case": "case_time_custom.csv",
                "parameters": {
                    "timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}
                },
                "externaldate": {
                    "from": {
                        "file": {"path": "file_6.json", "type": "json", "match": "uts"}
                    },
                    "mode": "add",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {"uts": {"value": 10000043140.0}},
            },
        ),
    ],
)
def test_datagram(input, ts, datadir):
    ret = datagram_from_input(input, "basiccsv", datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)
