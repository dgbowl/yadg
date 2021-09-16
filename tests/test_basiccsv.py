import pytest
import os
import json
from distutils import dir_util
from collections.abc import Iterable

from yadg import core

# tests for the basiccsv module:
#  - test_datagram_from_basiccsv:
#    - tests csv and ssv import
#    - tests that the correct number of lines is parsed
#    - tests that correct values are assigned
#    - tests specifying units in file and as dict

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
     {"nsteps": 1, "step": 0, "datalen": 6, "prop": "flow", "point": 0, 
      "sigma": True, "value": 15.0, "unit": "ml/min"}),
    ({"case": "case_timestamp.ssv", 
      "parameters": {"sep": ";", "units": {"flow": "ml/min", "T": "K", "p": "atm"}}}, 
     {"nsteps": 1, "step": 0, "datalen": 7, "prop": "flow", "point": 0, 
      "sigma": True, "value": 15.0, "unit": "ml/min"})
])
def test_datagram_from_basiccsv(input, ts, datadir):
    ret = datagram_from_basiccsv(input, datadir)
    assert len(ret) == ts["nsteps"]
    step = ret[ts["step"]]["results"]
    assert len(step) == ts["datalen"] 
    assert len(step[ts["point"]][ts["prop"]]) == 2 + int(ts["sigma"])
    assert step[ts["point"]][ts["prop"]][0] == ts["value"]
    assert step[ts["point"]][ts["prop"]][-1] == ts["unit"]

