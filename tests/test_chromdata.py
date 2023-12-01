import pytest
import os
import yaml
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
    dg_get_quantity,
)
from yadg.core import process_schema
from dgbowl_schemas.yadg import to_dataschema


def special_datagram_test(datagram, testspec):
    for i in {"height", "area", "concentration", "xout", "retention time"}:
        if i not in testspec:
            continue
        ret = dg_get_quantity(datagram, testspec["step"], i, testspec["point"])
        for k, v in testspec[i].items():
            rval = ret["n"].sel(dict(species=k))
            rdev = ret["s"].sel(dict(species=k))
            ru = ret["u"]
            print(f"{testspec[i]=}")
            print(f"{ret['n'].sel(dict(species=k))=}")
            compare_result_dicts({"n": rval, "s": rdev, "u": ru}, v)
        assert ret["n"].uts == testspec["uts"]


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
                "height": {
                    "MeOH": {"n": 0.0, "s": 1.0},
                },
                "area": {
                    "O2": {"n": 1034.53, "s": 0.01, "u": None},
                },
                "concentration": {
                    "CO": {"n": 0.02911539, "s": 0.0000291, "u": "%"},
                },
                "xout": {
                    "C2H6": {"n": 0.22425762, "s": 0.00022426, "u": "%"},
                },
                "retention time": {
                    "C2H6": {"n": 43.78, "s": 0.01, "u": "s"},
                },
                "uts": 1654697826.467,
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
                "height": {
                    "MeOH": {"n": 0.0, "s": 1.0},
                },
                "area": {
                    "O2": {"n": 1034.53, "s": 0.01},
                },
                "concentration": {
                    "CO": {"n": 0.02911539, "s": 0.0000291, "u": "%"},
                },
                "xout": {
                    "C2H6": {"n": 0.22425762, "s": 0.00022426, "u": "%"},
                },
                "retention time": {
                    "C2H6": {"n": 43.78, "s": 0.01, "u": "s"},
                },
                "uts": 1654697826.467,
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
                "area": {
                    "O2": {"n": 1034.53, "s": 0.001, "u": None},
                },
                "concentration": {
                    "CO": {"n": 0.02911539, "s": 1e-8, "u": "%"},
                },
                "xout": {
                    "C2H6": {"n": 0.22425762, "s": 1e-8, "u": "%"},
                },
                "retention time": {
                    "C2H6": {"n": 43.78, "s": 0.01, "u": "s"},
                },
                "uts": 1654697826.0,
            },
        ),
        (
            {  # ts2 - empalc.csv
                "folders": ["."],
                "suffix": "20p_v2.csv",
                "parameters": {
                    "filetype": "empalc.csv",
                },
                "externaldate": {"using": {"utsoffset": 0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 18,
                "method": "CO2RR_ChA_FTI_0.6mL_40uL_45dgr_32min.amx",
                "point": 17,
                "height": {
                    "Formic acid": {"n": 3436.903, "s": 0.001, "u": None},
                },
                "area": {
                    "Formic acid": {"n": 155913.098, "s": 0.001, "u": None},
                },
                "concentration": {
                    "Formic acid": {"n": 18.7521, "s": 0.0001, "u": "mmol/l"},
                },
                "retention time": {
                    "Formic acid": {"n": 15.671, "s": 0.001, "u": "min"},
                },
                "uts": 20400.0,
            },
        ),
        (
            {  # ts2 - empalc.csv
                "folders": ["."],
                "suffix": "25p_v2.csv",
                "parameters": {
                    "filetype": "empalc.csv",
                },
                "externaldate": {"using": {"utsoffset": 0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 19,
                "method": "CO2RR_ChA_FTI_0.6mL_40uL_45dgr_32min.amx",
                "point": 18,
                "height": {
                    "Ethanol": {"n": 25495.948, "s": 0.001, "u": None},
                },
                "area": {
                    "Ethanol": {"n": 2745541.097, "s": 0.001, "u": None},
                },
                "concentration": {
                    "Ethanol": {"n": 254.4736, "s": 0.0001, "u": "mmol/l"},
                },
                "retention time": {
                    "Ethanol": {"n": 21.098, "s": 0.001, "u": "min"},
                },
                "uts": 21600.0,
            },
        ),
        (
            {  # ts2 - empalc.xlsx
                "folders": ["."],
                "suffix": "25p_v2.xlsx",
                "parameters": {
                    "filetype": "empalc.xlsx",
                },
                "externaldate": {"using": {"utsoffset": 0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 19,
                "method": "CO2RR_ChA_FTI_0.6mL_40uL_45dgr_32min.amx",
                "point": 18,
                "height": {
                    "Ethanol": {"n": 25495.948, "s": 0.001},
                },
                "area": {
                    "Ethanol": {"n": 2745541.097, "s": 0.001, "u": None},
                },
                "concentration": {
                    "Ethanol": {"n": 254.4736, "s": 0.0001, "u": "mmol/l"},
                },
                "retention time": {
                    "Ethanol": {"n": 21.098, "s": 0.001, "u": "min"},
                },
                "uts": 21600.0,
            },
        ),
        (
            {  # ts3 - empalc.xlsx with newlines
                "folders": ["."],
                "suffix": "newlines.xlsx",
                "parameters": {
                    "filetype": "empalc.xlsx",
                },
                "externaldate": {"using": {"utsoffset": 0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 20,
                "method": "CO2RR_ChA_FTI_0.6mL_40uL_45dgr_32min.amx",
                "point": 18,
                "height": {
                    "Ethanol": {"n": 464.048, "s": 0.001},
                },
                "area": {
                    "Ethanol": {"n": 26514.098, "s": 0.001},
                },
                "concentration": {
                    "Ethanol": {"n": 2.4303, "s": 0.0001, "u": "mmol/l"},
                },
                "retention time": {
                    "Ethanol": {"n": 20.74, "s": 0.01, "u": "min"},
                },
                "uts": 21600.0,
            },
        ),
    ],
)
def test_datagram_from_chromdata(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromdata", datadir, version="4.2")
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)


def test_lock_stock_chromdata(datadir):
    os.chdir(datadir)
    with open("lock_stock_dataschema.yml", "r") as inf:
        schema = yaml.safe_load(inf)
    ret = process_schema(to_dataschema(**schema))
    print(f"{ret=}")
    for k in {"height", "concentration", "retention time", "area"}:
        assert ret["LC"][k].shape == (7, 2)
