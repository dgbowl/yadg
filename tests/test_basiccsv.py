import pytest
import os
import json
from distutils import dir_util
import datetime

from yadg import core

# tests for the basiccsv module:
#  - test_datagram_from_basiccsv:
#    - tests csv, ssv, tsv import
#    - tests that the correct number of lines is parsed depending on "units"
#    - tests that correct values are assigned to columns
#    - tests specifying units in file and as dict
#    - tests default rtol of 0.1%
#    - tests supplied atol and rtol for one variable
#    - tests implicit parsing of "uts" and "timestamp" fields
#    - tests explicit parsing of "uts" and "timestamp" fields with custom timestamp

@pytest.fixture
def datadir(tmpdir, request):
    """
    from: https://stackoverflow.com/a/29631801
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))
    return tmpdir

def datagram_from_basiccsv(input, datadir):
    schema = [{
        "datagram": "basiccsv",
        "import": {"files": [datadir.join(input["case"])]},
        "parameters": input.get("parameters", {})
    }]
    core.schema_validator(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"case": "case_uts_units.csv"},
     {"nsteps": 1, "step": 0, "nrows": 6, "prop": "flow", "point": 0, "sigma": 0.015, "value": 15.0, "unit": "ml/min"}),
    ({"case": "case_uts_units.csv",
      "parameters": {"timestamp": {"uts": 0}}}, 
     {"nsteps": 1, "step": 0, "nrows": 6, "prop": "uts", "point": 2, "value": 1631626610}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, "sigma": {"flow": {"rtol": 0.1}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "prop": "flow", "point": 0, "sigma": 1.5, "value": 15.0, "unit": "ml/min"}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, "timestamp": {"timestamp": 0}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "prop": "uts", "point": 3,
      "value": datetime.datetime(year=2021, month=9, day=10, hour=14, minute=33, second=25).timestamp()}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}, "sigma": {"T": {"atol": 0.05}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "T", "point": 3, "value": 351.2, "sigma": 0.05, "unit": "K"}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "uts", "point": 4,
      "value": datetime.datetime(year=2021, month=9, day=10, hour=13, minute=29, second=45).timestamp()}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "uts", "point": 2,
      "value": datetime.datetime(year=2021, month=9, day=10, hour=12, minute=29, second=45).timestamp()}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "uts", "point": 0,
      "value": datetime.datetime(year=2021, month=9, day=10, hour=11, minute=29, second=45).timestamp()}),
    ({"case": "case_date_time_iso.csv",
      "parameters": {"timestamp": {"date": 0, "time": 1}}}, 
     {"nsteps": 1, "step": 0, "nrows": 4, "prop": "uts", "point": 1,
      "value": datetime.datetime(year=2021, month=1, day=14, hour=21, minute=30, second=0).timestamp()}),
    ({"case": "case_time_custom.csv",
      "parameters": {"timestamp": {"time": [0, "%I.%M%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 3, "prop": "uts", "point": 0, "value": 43140}),
    ({"case": "case_time_custom.csv",
      "parameters": {"timestamp": {"time": [0, "%I.%M%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 3, "prop": "uts", "point": 1, "value": 43200}), 
])
def test_datagram_from_basiccsv(input, ts, datadir):
    ret = datagram_from_basiccsv(input, datadir)
    assert len(ret["data"]) == ts["nsteps"]
    step = ret["data"][ts["step"]]["timesteps"]
    assert len(step) == ts["nrows"]
    if ts["prop"] != "uts":
        assert len(step[ts["point"]][ts["prop"]]) == 3
        assert step[ts["point"]][ts["prop"]][0] == ts["value"]
        assert step[ts["point"]][ts["prop"]][1] == ts["sigma"]
        assert step[ts["point"]][ts["prop"]][2] == ts["unit"]
    else:
        assert step[ts["point"]][ts["prop"]] == ts["value"]
    

