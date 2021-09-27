import pytest
import os
import json
from distutils import dir_util
import datetime

from yadg import core
from general import object_is_datagram

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

def datagram_from_qftrace(input, datadir):
    schema = [{
        "datagram": "qftrace",
        "import": {"folders": [datadir]},
        "parameters": input.get("parameters", {})
    }]
    core.schema_validator(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    
    ({"parameters": {"method": "naive"}},
     {"nsteps": 1, "step": 0, "ntimesteps": 1, "timestep": 0, "tracelen": 20001, 
      "npeaks": 2, "peak": 0, "Q": 2626.506, "f": 7173245000.0}),  
    ({"parameters": {"method": "naive", "threshold": 1e-7}},
     {"nsteps": 1, "step": 0, "ntimesteps": 1, "timestep": 0, "tracelen": 20001, 
      "npeaks": 2, "peak": 0, "Q": 2567.343, "f": 7173245000.0}),  
    ({"parameters": {"method": "lorentz"}},
     {"nsteps": 1, "step": 0, "ntimesteps": 1, "timestep": 0, "tracelen": 20001, 
      "npeaks": 2, "peak": 0, "Q": 3093.853, "f": 7173256009.5}),
    ({"parameters": {"method": "kajfez"}},
     {"nsteps": 1, "step": 0, "ntimesteps": 1, "timestep": 0, "tracelen": 20001, 
      "npeaks": 2, "peak": 0, "Q": 3061.156, "f": 7173122656.1}),
    ({"parameters": {"method": "kajfez", "cutoff": 0.5}},
     {"nsteps": 1, "step": 0, "ntimesteps": 1, "timestep": 0, "tracelen": 20001, 
      "npeaks": 2, "peak": 0, "Q": 3054.886, "f": 7173125153.7}),
])
def test_datagram_from_qftrace(input, ts, datadir):
    ret = datagram_from_qftrace(input, datadir)
    object_is_datagram(ret)
    assert len(ret["data"]) == ts["nsteps"]
    step = ret["data"][ts["step"]]
    assert len(step["timesteps"]) == ts["ntimesteps"]
    tstep = step["timesteps"][ts["timestep"]]
    assert len(tstep["trace"]["f"]) == ts["tracelen"] and \
           len(tstep["trace"]["Γ"]) == ts["tracelen"] and \
           len(tstep["trace"]["abs(Γ)"]) == ts["tracelen"]
    assert tstep["npeaks"] == ts["npeaks"]
    assert len(tstep["Q"]) == ts["npeaks"]
    assert len(tstep["f"]) == ts["npeaks"]
    assert tstep["Q"][ts["peak"]][0] == pytest.approx(ts["Q"], abs = 1)
    assert tstep["f"][ts["peak"]][0] == pytest.approx(ts["f"], abs = 10)
    assert 1/tstep["Q"][1][0] - 1/tstep["Q"][0][0] == pytest.approx(0.00035, abs = 0.00005)
    
