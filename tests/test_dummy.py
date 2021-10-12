import pytest
import os
import json
from distutils import dir_util

from yadg import core
from schemas import dummy_1, dummy_2, dummy_3, dummy_4, dummy_5
from schemas import fail_1, fail_2, fail_3, fail_4, fail_5

# tests for the dummy module:
#  - test_datagram_from_schema_dict:
#    - tests creating datagrams from a dictionary
#    - tests path parsing for folders, files
#    - tests path parsing for prefix, suffix, contains
#  - test_datagram_from_schema_path:
#    - tests creating datagrams from a json file
#    - tests path parsing for folders, files and paths
#    - tests passing parameters as kwargs
#  - test_schema_validator:
#    - makes sure schema_validator throws correct exceptions

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

def datagram_from_schema_file(inp_fn, datadir):
    jsonpath = datadir.join(inp_fn)
    with open(jsonpath, "r") as infile:
        schema = json.load(infile)
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

def datagram_from_schema_dict(schema):
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

@pytest.mark.parametrize("inp_dict, l_dg, l_res", [
    (dummy_1, 1, 0),
    (dummy_2, 1, 1),
    (dummy_3, 1, 2), 
    (dummy_4, 1, 2),
    (dummy_5, 1, 1)
])
def test_datagram_from_schema_dict(inp_dict, l_dg, l_res, datadir):
    os.chdir(datadir)
    ret = datagram_from_schema_dict(inp_dict)
    assert core.validators.validate_datagram(ret)
    assert len(ret["data"]) == l_dg
    if l_dg > 0:
        assert len(ret["data"][0]["timesteps"]) == l_res
    json.dumps(ret)

@pytest.mark.parametrize("inp_fn, ts", [
    ("dummy_schema_1.json", {"nsteps": 1, "step": 0, "item": 0, "kwargs": {}}),
    ("dummy_schema_2.json", {"nsteps": 2, "step": 1, "item": 0, "kwargs": {"k": "v"}})
])
def test_datagram_from_schema_file(inp_fn, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_schema_file(inp_fn, datadir)
    assert core.validators.validate_datagram(ret)
    assert len(ret["data"]) == ts["nsteps"]
    assert ret["data"][ts["step"]]["timesteps"][ts["item"]]["raw"] == ts["kwargs"]
    json.dumps(ret)

@pytest.mark.parametrize("inp_dict, expr", [
    (fail_1, r"'parser'"),
    (fail_2, r"'dumm'"),
    (fail_3, r"2 were provided"),
    (fail_4, r"0 were provided"),
    (fail_5, r"'key'"),
])
def test_schema_validator(inp_dict, expr, datadir):
    os.chdir(datadir)
    with pytest.raises(AssertionError, match = expr):
        assert core.validators.validate_schema(inp_dict)
    