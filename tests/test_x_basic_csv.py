import pytest
import os
import pickle
from yadg.extractors.basic.csv import extract
from dgbowl_schemas.yadg.dataschema_5_1.filetype import Basic_csv
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile, params",
    [
        (
            "case_uts_units.csv",
            {"timestamp": {"uts": {"index": 0}}},
        ),
        (
            "case_timestamp.ssv",
            {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}},
        ),
        (
            "case_custom_ts.tsv",
            {
                "sep": "\t",
                "timestamp": {
                    "timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}
                },
            },
        ),
        (
            "picolog_temperature.csv",
            {
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
        ),
        (
            "picolog_temperature_sparse.csv",
            {
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
        ),
        (
            "flow_data.csv",
            {
                "sep": ",",
                "timestamp": {"time": {"index": 5}},
                "units": {
                    "DryCal smL/min": "smL/min",
                    "DryCal Avg. smL/min": "smL/min",
                    "Temp. Deg C": "degC",
                    "Pressure mBar": "mbar",
                },
            },
        ),
    ],
)
def test_basic_csv(infile, params, datadir):
    os.chdir(datadir)
    ret = extract(
        fn=infile,
        parameters=Basic_csv(filetype="basic.csv", parameters={**params}).parameters,
        encoding="utf8",
        locale="en_GB",
        timezone="Europe/Berlin",
    )
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)


@pytest.mark.parametrize(
    "infile, params, locale",
    [
        (
            "sheet.UK.tsv",
            {
                "sep": "\t",
                "timestamp": {
                    "date": {"index": 0, "format": "%d/%m/%Y"},
                    "time": {"index": 1, "format": "%H:%M:%S"},
                },
            },
            "en_GB.UTF-8",
        ),
        (
            "sheet.DE.tsv",
            {
                "sep": "\t",
                "timestamp": {
                    "date": {"index": 0, "format": "%d.%m.%Y"},
                    "time": {"index": 1, "format": "%H:%M:%S"},
                },
            },
            "de_DE.UTF-8",
        ),
        (
            "sheet.US.tsv",
            {
                "sep": "\t",
                "timestamp": {
                    "date": {"index": 0, "format": "%m/%d/%Y"},
                    "time": {"index": 1, "format": "%H:%M:%S %p"},
                },
            },
            "en_US.UTF-8",
        ),
    ],
)
def test_basic_csv_locale(infile, params, locale, datadir):
    os.chdir(datadir)
    ret = extract(
        fn=infile,
        parameters=Basic_csv(filetype="basic.csv", parameters={**params}).parameters,
        encoding="utf8",
        locale=locale,
        timezone="Europe/Berlin",
    )
    outfile = "sheet.XX.tsv.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)


@pytest.mark.parametrize(
    "infile, params, encoding",
    [
        (
            "log 2021-09-17 11-26-14.140.csv",
            {
                "timestamp": {
                    "timestamp": {"index": 0, "format": '"%Y-%m-%d %H:%M:%S.%f"'}
                },
                "units": {},
            },
            "utf-8-sig",
        ),
    ],
)
def test_basic_csv_encoding(infile, params, encoding, datadir):
    os.chdir(datadir)
    ret = extract(
        fn=infile,
        parameters=Basic_csv(filetype="basic.csv", parameters={**params}).parameters,
        encoding=encoding,
        locale="en_GB",
        timezone="Europe/Berlin",
    )
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
