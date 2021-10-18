import pytest
import os
import json
from distutils import dir_util

from yadg import core

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
        "metadata": {"provenance": "manual", "schema_version": "0.1", "timezone": "UTC"},
        "steps": [{
          "parser": input["parser"],
          "import": {"files": input["files"], "encoding": input["encoding"]},
          "parameters": input.get("parameters", {})
        }]
    }
    os.chdir(datadir)
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("input, ts", [
    ({"files": ["log 2021-09-17 11-26-14.140.csv"], "parser": "basiccsv", "encoding": "utf-8-sig", 
      "parameters": {"timestamp": {"timestamp": {"index": 0, "format": "\"%Y-%m-%d %H:%M:%S.%f\""}}, "units": {}}},
     {"nsteps": 1, "step": 0, "nrows": 239, "point": 0, "pars": {"uts": {"value": 1631877974.045}}}),
])
def test_datagram(input, ts, datadir):
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
    

