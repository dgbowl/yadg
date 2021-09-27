import pytest
import os
import json
from distutils import dir_util

from yadg import core
from general import object_is_datagram
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
    schema = [{
        "datagram": "gctrace",
        "import": {"folders": ["."], 
                   "prefix": input["prefix"],
                   "suffix": input["suffix"]},
        "parameters": input.get("parameters", {})
    }]
    core.schema_validator(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    #({"prefix": "2019-12-03", "suffix": "dat.asc", 
    #  "parameters": {"tracetype": "datasc", "calfile": "gc_5890_FHI.json"},},
    # {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "polyarc+TCD_PK_09b.met", "xout": {"propane": 0.022, "N2": 0.915}}),  
    #({"prefix": "CHROMTAB", "suffix": "CSV", 
    #  "parameters": {"tracetype": "chromtab", "calfile": "gc_chromtab.json"},},
    # {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "n/a", "xout": {"N2": 0.74}}),   
    #({"prefix": "CHROMTAB", "suffix": "CSV", 
    #  "parameters": {"tracetype": "chromtab", "species": gctrace_chromtab["sp"], "detectors": gctrace_chromtab["det"]},},
    # {"nsteps": 1, "step": 0, "ntsteps": 3, "method": "n/a", "xout": {"N2": 0.74}}),    
    ({"prefix": "", "suffix": "fusion-data", 
      "parameters": {"tracetype": "fusion", "calfile": "gc_fusion.json"},},
     {"nsteps": 1, "step": 0, "ntsteps": 5, "method": "n/a", "xout": {"N2": 0.74}}),    
])
def test_datagram_from_gctrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_gctrace(input, datadir)
    object_is_datagram(ret)
    for ts in ret["data"][0]["timesteps"]:
        print(ts["peaks"]["TCD1"].get("H2", ""))
    assert False
    assert len(ret["data"]) == ts["nsteps"]
    step = ret["data"][ts["step"]]
    assert step["metadata"]["gcparams"]["method"].endswith(ts["method"])
    assert len(step["timesteps"]) == ts["ntsteps"]
    for tstep in step["timesteps"]:
        print(tstep["xout"])
        for k, v in ts["xout"].items():
            assert tstep["xout"][k][0] == pytest.approx(v, rel = 0.02)
