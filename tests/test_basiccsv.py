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
    schema = {
        "metadata": {"provenance": "manual", "schema_version": "0.1"},
        "steps": [{
          "parser": "basiccsv",
          "import": {"files": [input["case"]]},
          "parameters": input.get("parameters", {})
        }]
    }
    os.chdir(datadir)
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"case": "case_uts_units.csv"},
     {"nsteps": 1, "step": 0, "nrows": 6, "point": 0, "pars": {"flow": {"sigma": 0.0, "value": 15.0, "unit": "ml/min"}}}),
    ({"case": "case_uts_units.csv",
      "parameters": {"timestamp": {"uts": {"index": 0}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 6, "point": 2, "pars": {"uts": {"value": 1631626610.0}}}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, "sigma": {"flow": {"rtol": 0.1}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "point": 0, "pars": {"flow": {"sigma": 1.5, "value": 15.0, "unit": "ml/min"}}}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, "timestamp": {"timestamp": {"index": 0}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "point": 3, "pars": {"uts": {"value": 1631284405.0}}}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}}, "sigma": {"T": {"atol": 0.05}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "point": 3, "pars": {"T": {"value": 351.2, "sigma": 0.05, "unit": "K"}}}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "point": 4, "pars": {"uts": {"value": 1631280585.0}}}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "point": 2, "pars": {"uts": {"value": 1631276985.0}}}),
    ({"case": "case_custom_ts.tsv",
      "parameters": {"sep": "\t", "timestamp": {"timestamp": {"index": 1, "format": "%d.%m.%Y %I:%M:%S%p"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 5, "point": 0, "pars": {"uts": {"value": 1631273385.0}}}),
    ({"case": "case_date_time_iso.csv",
      "parameters": {"timestamp": {"date": {"index": 0}, "time": {"index": 1}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 4, "point": 1, "pars": {"uts": {"value": 1610659800.0}}}),
    ({"case": "case_time_custom.csv",
      "parameters": {"timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 3, "point": 0, "pars": {"uts": {"value": 43140}}}),
    ({"case": "case_time_custom.csv",
      "parameters": {"timestamp": {"time": {"index": 0, "format": "%I.%M%p"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 3, "point": 1, "pars": {"uts": {"value": 43200}}}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}, 
      "convert": {"flow": {"flow": {"calib": {"linear": {"slope": 1e-6/60}, "atol": 1e-8}}, "unit": "m3/s"}}}}, 
     {"nsteps": 1, "step": 0, "nrows": 7, "point": 0, "pars": {"flow": {"sigma": 1e-8, "value": 2.5e-7, "unit": "m3/s", "raw": False}}}),
    ({"case": "case_uts_units.csv",
      "parameters": {"atol": 0.1, "convert": {"T": {"T": {"calib": {"linear": {"intercept": 273.15}}}, "unit": "K"}}}},
     {"nsteps": 1, "step": 0, "nrows": 6, "point": 0, "pars": {"T": {"sigma": 0.1, "value": 296.25, "unit": "K", "raw": False}}}),
    ({"case": "case_uts_units.csv",
      "parameters": {"atol": 0.1, "calfile": "calib.json"}},
     {"nsteps": 1, "step": 0, "nrows": 6, "point": 0, "pars": {"T": {"sigma": 0.1, "value": 296.25, "unit": "K", "raw": False}}}),
    ({"case": "measurement.csv",
      "parameters": {"sep": ";", "timestamp": {"timestamp": {"index": 0, "format": "%Y-%m-%d-%H-%M-%S"}}, "calfile": "tfcal.json"}},
     {"nsteps": 1, "step": 0, "nrows": 1662, "point": 0, "pars": {"C3H8": {"sigma": 0.0, "value": 0.0, "unit": "ml/min", "raw": False}, "N2": {"sigma": 0.0, "value": 30.361, "unit": "ml/min", "raw": False}, "O2": {"sigma": 0.0, "value": 1.579, "unit": "ml/min", "raw": False}}}),
    ({"case": "measurement.csv",
      "parameters": {"sep": ";", "timestamp": {"timestamp": {"index": 0, "format": "%Y-%m-%d-%H-%M-%S"}}, "calfile": "tfcal.json"}},
     {"nsteps": 1, "step": 0, "nrows": 1662, "point": 100, "pars": {"C3H8": {"sigma": 0.0, "value": 1.204, "unit": "ml/min", "raw": False}, "N2": {"sigma": 0.0, "value": 35.146, "unit": "ml/min", "raw": False}, "O2": {"sigma": 0.0, "value": 3.577, "unit": "ml/min", "raw": False}}}),
])
def test_datagram_from_basiccsv(input, ts, datadir):
    ret = datagram_from_basiccsv(input, datadir)
    assert core.validators.validate_datagram(ret)
    assert len(ret["data"]) == ts["nsteps"]
    steps = ret["data"][ts["step"]]["timesteps"]
    assert len(steps) == ts["nrows"]
    tstep = steps[ts["point"]]
    for tk, tv in ts["pars"].items():
        if tk != "uts":
            print(tv)
            rd = "raw" if tv.get("raw", True) else "derived"
            assert len(tstep[rd][tk]) == 3
            assert tstep[rd][tk][0] == pytest.approx(tv["value"], abs = 0.001)
            assert tstep[rd][tk][1] == pytest.approx(tv["sigma"], rel = 0.1)
            assert tstep[rd][tk][2] == tv["unit"]
        else:
            assert tstep[tk] == tv["value"]
    json.dumps(ret)
    

