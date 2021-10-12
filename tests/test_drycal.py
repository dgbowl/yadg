import pytest
import os
import json
from distutils import dir_util

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

def datagram_from(input, datadir):
    schema = {
        "metadata": {"provenance": "manual", "schema_version": "0.1"},
        "steps": [{
          "parser": "drycal",
          "import": {"files": [input["case"]]},
          "parameters": input.get("parameters", {})
        }]
    }
    os.chdir(datadir)
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"case": "Cp_100mA_1mindelay.rtf", 
     "parameters": {"date": "2021-09-17"}},
     {"nsteps": 1, "step": 0, "nrows": 110, "point": 0, "pars": {"Temp": {"sigma": 0.0, "value": 27.4, "unit": "Deg C"}}}),
    ({"case": "20211011_DryCal_out.csv"},
     {"nsteps": 1, "step": 0, "nrows": 29, "point": 0, "pars": {"Temp": {"sigma": 0.0, "value": 24.3, "unit": "Deg C"}}}),
    ({"case": "2021-10-11_DryCal_out.txt"},
     {"nsteps": 1, "step": 0, "nrows": 29, "point": 28, "pars": {"Pressure": {"sigma": 0.0, "value": 971.0, "unit": "mBar"}}})   
])
def test_datagram_from_drycal(input, ts, datadir):
    ret = datagram_from(input, datadir)
    assert core.validators.validate_datagram(ret)
    assert len(ret["data"]) == ts["nsteps"]
    steps = ret["data"][ts["step"]]["timesteps"]
    assert len(steps) == ts["nrows"]
    tstep = steps[ts["point"]]
    for tk, tv in ts["pars"].items():
        if tk != "uts":
            rd = "raw" if tv.get("raw", True) else "derived"
            assert len(tstep[rd][tk]) == 3
            assert tstep[rd][tk][0] == pytest.approx(tv["value"], abs = 0.001)
            assert tstep[rd][tk][1] == pytest.approx(tv["sigma"], rel = 0.1)
            assert tstep[rd][tk][2] == tv["unit"]
        else:
            assert tstep[tk] == tv["value"]
    json.dumps(ret)
    

