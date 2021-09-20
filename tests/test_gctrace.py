import pytest
import os
import json
from distutils import dir_util
import datetime

from yadg import core

# tests for the basiccsv module:
#  - test_datagram_from_qftrace:
#    - tests processing using the "naive", "lorentz", and "kajfez" fitters
#    - tests passing "cutoff" parameter to the "kajfez" fitter
#    - tests passing "threshold" parameter to "naive" fitter

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

def datagram_from_gctrace(input, datadir):
    schema = [{
        "datagram": "gctrace",
        "import": {"folders": [datadir], "suffix": "dat.asc"},
        "parameters": input.get("parameters", {})
    }]
    core.schema_validator(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"parameters": {"tracetype": "datasc", "species": {}, "detectors": {}}},
     {"nsteps": 1, "step": 0, "ntimesteps": 1, "timestep": 0, "tracelen": 20001, 
      "npeaks": 2, "peak": 0, "Q": 2626.506, "f": 7173245000.0}),  
])
def test_datagram_from_gctrace(input, ts, datadir):
    ret = datagram_from_gctrace(input, datadir)
    print(ret)
    assert False