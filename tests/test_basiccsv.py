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
        "parser": "basiccsv",
        "import": {"files": [str(datadir.join(input["case"]))]},
        "parameters": input.get("parameters", {})
    }]
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"case": "case_uts_units.csv"},
     {"nsteps": 1, "step": 0, "nrows": 6, "prop": "flow", "point": 0, "sigma": 0.0, "value": 15.0, "unit": "ml/min"}),
    ({"case": "case_uts_units.csv",
      "parameters": {"timestamp": {"uts": 0}}}, 
     {"nsteps": 1, "step": 0, "nrows": 6, "prop": "uts", "point": 2, "value": 1631626610.0}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, "sigma": {"flow": {"rtol": 0.1}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "prop": "flow", "point": 0, "sigma": 1.5, "value": 15.0, "unit": "ml/min"}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, "timestamp": {"timestamp": 0}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "prop": "uts", "point": 3, "value": 1631284405.0}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}, "sigma": {"T": {"atol": 0.05}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "T", "point": 3, "value": 351.2, "sigma": 0.05, "unit": "K"}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "uts", "point": 4, "value": 1631280585.0}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "uts", "point": 2, "value": 1631276985.0}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": [1, "%d.%m.%Y %I:%M:%S%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "prop": "uts", "point": 0, "value": 1631273385.0}),
    ({"case": "case_date_time_iso.csv",
      "parameters": {"timestamp": {"date": 0, "time": 1}}}, 
     {"nsteps": 1, "step": 0, "nrows": 4, "prop": "uts", "point": 1, "value": 1610659800.0}),
    ({"case": "case_time_custom.csv",
      "parameters": {"timestamp": {"time": [0, "%I.%M%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 3, "prop": "uts", "point": 0, "value": 43140}),
    ({"case": "case_time_custom.csv",
      "parameters": {"timestamp": {"time": [0, "%I.%M%p"]}}}, 
     {"nsteps": 1, "step": 0, "nrows": 3, "prop": "uts", "point": 1, "value": 43200}), 
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, 
      "convert": {"flow": {"header": "flow", "calib": {"linear": {"slope": 1e-6/60}, "atol": 1e-8}, "unit": "m3/s"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "prop": "flow", "point": 0, "sigma": 1e-8, "value": 2.5e-7, "unit": "m3/s"}),
    ({"case": "case_uts_units.csv",
      "parameters": {"atol": 0.1, "convert": {"T": {"header": "T", "calib": {"linear": {"intercept": 273.15}}, "unit": "K"}}}},
     {"nsteps": 1, "step": 0, "nrows": 6, "prop": "T", "point": 0, "sigma": 0.1, "value": 296.25, "unit": "K"}),
])
def test_datagram_from_basiccsv(input, ts, datadir):
    ret = datagram_from_basiccsv(input, datadir)
    assert core.validators.validate_datagram(ret)
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
    json.dumps(ret)
    

