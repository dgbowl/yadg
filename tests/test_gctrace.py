import pytest
import os
import json
from distutils import dir_util

from yadg import core
from schemas import gctrace_chromtab

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
    schema =  {
        "metadata": {"provenance": "manual", "schema_version": "0.1"},
        "steps": [{
            "parser": "gctrace",
            "import": {
                "folders": ["."], "prefix": input["prefix"], "suffix": input["suffix"]
                },
            "parameters": input.get("parameters", {})
        }]
    }
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"prefix": "2019-12-03", "suffix": "dat.asc", 
      "parameters": {"tracetype": "datasc", "calfile": "gc_5890_FHI.json"},},
     {"nsteps": 1, "step": 0, "ntsteps": 5, "method": "polyarc+TCD_PK_09b.met", 
      "tstep": 1, "xout": {"O2": 0.046, "propane": 0.023, "N2": 0.918}}),  
    ({"prefix": "2019-12-03", "suffix": "dat.asc", 
      "parameters": {"tracetype": "datasc", "calfile": "gc_5890_FHI.json"},},
     {"nsteps": 1, "step": 0, "ntsteps": 5, "method": "polyarc+TCD_PK_09b.met", 
      "tstep": 4, "xout": {"O2": 0.036, "propane": 0.022, "N2": 0.915}}),  
    ({"prefix": "CHROMTAB", "suffix": "CSV", 
      "parameters": {"tracetype": "chromtab", "calfile": "gc_chromtab.json"},},
     {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "n/a", 
      "tstep": 2, "xout": {"N2": 0.674, "CH3OH": 0.320}}),   
    ({"prefix": "CHROMTAB", "suffix": "CSV", 
      "parameters": {"tracetype": "chromtab", "species": gctrace_chromtab["sp"], "detectors": gctrace_chromtab["det"]},},
     {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "n/a", 
      "tstep": 0, "xout": {"N2": 0.647, "CH3OH": 0.343}}),    
    ({"prefix": "", "suffix": "fusion-data", 
      "parameters": {"tracetype": "fusion", "calfile": "gc_fusion.json"}},
     {"nsteps": 1, "step": 0, "ntsteps": 5, "method": "AS_Cal_20210702",
      "tstep": 0, "xout": {"H2": 0.994, "CO": 0.006}}),    
    ({"prefix": "", "suffix": "fusion-data", 
      "parameters": {"tracetype": "fusion", "calfile": "gc_fusion.json"}},
     {"nsteps": 1, "step": 0, "ntsteps": 5, "method": "AS_Cal_20210702",
      "tstep": 4, "xout": {"H2": 0.029, "CO2": 0.971}}),    
])
def test_datagram_from_gctrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_gctrace(input, datadir)
    assert core.validators.validate_datagram(ret)
    assert len(ret["data"]) == ts["nsteps"]
    step = ret["data"][ts["step"]]
    assert step["metadata"]["gcparams"]["method"].endswith(ts["method"])
    assert len(step["timesteps"]) == ts["ntsteps"]
    tstep = step["timesteps"][ts["tstep"]]
    for k, v in ts["xout"].items():
        assert tstep["derived"]["xout"][k][0] == pytest.approx(v, abs = 0.001)
    json.dumps(ret)
