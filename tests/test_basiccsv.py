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
            {  # ts11 - convert functionality test
                "case": "case_timestamp.ssv",
                "parameters": {
                    "sep": ";",
                    "units": {"flow": "ml/min", "T": "K", "p": "atm"},
                    "convert": {
                        "flow": {
                            "flow": {
                                "calib": {"linear": {"slope": 1e-6 / 60}, "atol": 1e-8}
                            },
                            "unit": "m^3/s",
                        }
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "point": 0,
                "pars": {
                    "flow": {
                        "sigma": 1e-8,
                        "value": 2.5e-7,
                        "unit": "m^3/s",
                        "raw": False,
                    },
                },
            },
        ),
        (
            {  # ts12 - convert functionality with intercept only and both global and calib sigma
                "case": "case_uts_units.csv",
                "parameters": {
                    "convert": {
                        "T": {
                            "T": {
                                "calib": {"linear": {"intercept": 273.15}, "atol": 0.5}
                            },
                            "unit": "K",
                        }
                    },
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 6,
                "point": 0,
                "pars": {
                    "T": {"sigma": 0.5, "value": 296.25, "unit": "K", "raw": False},
                },
            },
        ),
        (
            {  # ts13 - calfile functionality
                "case": "case_uts_units.csv",
                "parameters": {"calfile": "calibrations/test_calib.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 6,
                "point": 0,
                "pars": {
                    "T": {"sigma": 0.1, "value": 296.25, "unit": "K", "raw": False}
                },
            },
        ),
        (
            {  # ts14 - calfile functionality with fractions and total
                "case": "data_3.1.0/00-experiment/measurement.csv",
                "parameters": {
                    "sep": ";",
                    "timestamp": {
                        "timestamp": {"index": 0, "format": "%Y-%m-%d-%H-%M-%S"}
                    },
                    "calfile": "calibrations/fhi_tfcal.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1662,
                "point": 0,
                "pars": {
                    "C3H8": {
                        "sigma": 0.002,
                        "value": 0.000,
                        "unit": "ml/min",
                        "raw": False,
                    },
                    "N2": {
                        "sigma": 0.01351715237,
                        "value": 30.36065211976,
                        "unit": "ml/min",
                        "raw": False,
                    },
                    "O2": {
                        "sigma": 0.01092061507,
                        "value": 1.57860743175,
                        "unit": "ml/min",
                        "raw": False,
                    },
                    "Total": {
                        "sigma": 0.0323269088,
                        "value": 31.9392595515,
                        "unit": "ml/min",
                        "raw": False,
                    },
                },
            },
        ),
        (
            {  # ts15 - calfile functionality with fractions and total
                "case": "data_3.1.0/00-experiment/measurement.csv",
                "parameters": {
                    "sep": ";",
                    "timestamp": {
                        "timestamp": {"index": 0, "format": "%Y-%m-%d-%H-%M-%S"}
                    },
                    "calfile": "calibrations/fhi_tfcal.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1662,
                "point": 100,
                "pars": {
                    "C3H8": {
                        "sigma": 0.00157299296,
                        "value": 1.20450873872,
                        "unit": "ml/min",
                        "raw": False,
                    },
                    "N2": {
                        "sigma": 0.01258182490,
                        "value": 35.1460003698,
                        "unit": "ml/min",
                        "raw": False,
                    },
                    "O2": {
                        "sigma": 0.01092061507,
                        "value": 3.57707998956,
                        "unit": "ml/min",
                        "raw": False,
                    },
                    "Total": {
                        "sigma": 0.03683714813,
                        "value": 39.9275890981,
                        "unit": "ml/min",
                        "raw": False,
                    },
                },
            },
        ),
        (
            {  # ts16 - test stripping
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
                        "raw": True,
                    }
                },
            },
        ),
        (
            {  # ts17 - test sparse tables
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
                        "raw": True,
                    },
                    "Inside_Nafion_TCK02 Max. (C)": {
                        "value": None,
                        "raw": True,
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
