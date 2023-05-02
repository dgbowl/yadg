import pytest
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    pars_datagram_test,
)
import numpy as np


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - units on 2nd line, correct number of rows, correct value, sigma from d.p.
                "case": "case_uts_units.csv"
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 6,
                "point": 0,
                "pars": {"flow": {"sigma": 0.1, "value": 15.0, "unit": "ml/min"}},
            },
        ),
        (
            {  # ts1 - timestamp from uts and index
                "case": "case_uts_units.csv",
                "parameters": {"timestamp": {"uts": {"index": 0}}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 6,
                "point": 2,
                "pars": {"uts": {"value": 1631626610.0}},
            },
        ),
        (
            {  # ts2 - semicolon separator, sigmas from decimal places
                "case": "case_timestamp.ssv",
                "parameters": {
                    "sep": ";",
                    "units": {"flow": "ml/min", "T": "K", "p": "atm"},
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {
                    "flow": {"sigma": 0.1, "value": 15.0, "unit": "ml/min"},
                    "T": {"sigma": 0.1, "value": 23.1, "unit": "K"},
                    "p": {"sigma": 0.0001, "value": 1.0001, "unit": "atm"},
                },
            },
        ),
        (
            {  # ts3 - semicolon separator, timestamp from timestamp and index
                "case": "case_timestamp.ssv",
                "parameters": {
                    "sep": ";",
                    "units": {"flow": "ml/min", "T": "K", "p": "atm"},
                    "timestamp": {"timestamp": {"index": 0}},
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 1,
                "pars": {"uts": {"value": 1631284345.0}},
            },
        ),
        (
            {  # ts4 - tab separator
                "case": "case_custom_ts.tsv",
                "parameters": {
                    "sep": "\t",
                    "timestamp": {
                        "timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "point": 3,
                "pars": {"T": {"value": 351.2, "sigma": 0.1, "unit": "K"}},
            },
        ),
        (
            {  # ts5 - tab separator, timestamp from timestamp, format, index
                "case": "case_custom_ts.tsv",
                "parameters": {
                    "sep": "\t",
                    "timestamp": {
                        "timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "point": 4,
                "pars": {"uts": {"value": 1631280585.0}},
            },
        ),
        (
            {  # ts6 - tab separator, timestamp from timestamp, format, index
                "case": "case_custom_ts.tsv",
                "parameters": {
                    "sep": "\t",
                    "timestamp": {
                        "timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "point": 2,
                "pars": {"uts": {"value": 1631276985.0}},
            },
        ),
        (
            {  # ts7 - tab separator, timestamp from timestamp, format, index
                "case": "case_custom_ts.tsv",
                "parameters": {
                    "sep": "\t",
                    "timestamp": {
                        "timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "point": 0,
                "pars": {"uts": {"value": 1631273385.0}},
            },
        ),
        (
            {  # ts8 - tab separator, timestamp from iso date and iso time
                "case": "case_date_time_iso.csv",
                "parameters": {
                    "timestamp": {"date": {"index": 0}, "time": {"index": 1}}
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 4,
                "point": 1,
                "pars": {"uts": {"value": 1610659800.0}},
            },
        ),
        (
            {  # ts9 - timestamp from time with external date only
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
            {  # ts10 - timestamp from time with custom format only
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
                "point": 1,
                "pars": {"uts": {"value": 43200}},
            },
        ),
        (
            {  # ts11 - test stripping
                "case": "picolog_temperature.csv",
                "version": "4.2",
                "parameters": {
                    "sep": ",",
                    "timestamp": {"uts": {"index": 0}},
                    "strip": '"',
                    "units": {
                        "Outside Last (C)": "degC",
                        "Outside Ave. (C)": "degC",
                        "Outside Min. (C)": "degC",
                        "Outside Max. (C)": "degC",
                        "Inside_GDE_TCK01 Last (C)": "degC",
                        "Inside_GDE_TCK01 Ave. (C)": "degC",
                        "Inside_GDE_TCK01 Min. (C)": "degC",
                        "Inside_GDE_TCK01 Max. (C)": "degC",
                        "Inside_Nafion_TCK02 Last (C)": "degC",
                        "Inside_Nafion_TCK02 Ave. (C)": "degC",
                        "Inside_Nafion_TCK02 Min. (C)": "degC",
                        "Inside_Nafion_TCK02 Max. (C)": "degC",
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 2470,
                "point": 2469,
                "pars": {
                    "Outside Last (C)": {
                        "sigma": 0.01,
                        "value": 26.14,
                        "unit": "degC",
                    }
                },
            },
        ),
        (
            {  # ts12 - test sparse tables
                "case": "picolog_temperature_sparse.csv",
                "version": "4.2",
                "parameters": {
                    "sep": ",",
                    "timestamp": {"uts": {"index": 0}},
                    "strip": '"',
                    "units": {
                        "Outside Last (C)": "degC",
                        "Outside Ave. (C)": "degC",
                        "Outside Min. (C)": "degC",
                        "Outside Max. (C)": "degC",
                        "Inside_GDE_TCK01 Last (C)": "degC",
                        "Inside_GDE_TCK01 Ave. (C)": "degC",
                        "Inside_GDE_TCK01 Min. (C)": "degC",
                        "Inside_GDE_TCK01 Max. (C)": "degC",
                        "Inside_Nafion_TCK02 Last (C)": "degC",
                        "Inside_Nafion_TCK02 Ave. (C)": "degC",
                        "Inside_Nafion_TCK02 Min. (C)": "degC",
                        "Inside_Nafion_TCK02 Max. (C)": "degC",
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 2226,
                "point": 361,
                "pars": {
                    "Outside Last (C)": {
                        "sigma": 0.01,
                        "value": 25.97,
                        "unit": "degC",
                    },
                    "Inside_Nafion_TCK02 Max. (C)": {
                        "value": np.nan,
                        "sigma": np.nan,
                        "unit": "degC",
                    },
                },
            },
        ),
    ],
)
def test_datagram_from_basiccsv(input, ts, datadir):
    ver = input.pop("version", "4.0")
    ret = datagram_from_input(input, "basiccsv", datadir, version=ver)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)
