import pytest
import os
import json
from distutils import dir_util
from collections.abc import Iterable

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

def datagram_from_schema_file(inp_fn, datadir):
    jsonpath = datadir.join(inp_fn)
    with open(jsonpath, "r") as infile:
        schema = json.load(infile)
    return core.process_schema(schema, permissive = True)

def datagram_from_schema_path(inp_dict, datadir):
    inp_dict["import"]["paths"] = [datadir.join(i) for i in inp_dict["import"]["paths"]]
    return core.process_schema([inp_dict], permissive = True)


dict_1 = {
    "datagram": "dummy",
    "import": {
        "paths": ["dummy_schema_1"]
    }
}

dict_2 = {
    "datagram": "dummy",
    "import": {
        "paths": ["dummy_schema_2.json"]
    }
}

@pytest.mark.parametrize("inp_dict, tf", [
    (dict_1, False),
    (dict_2, True)
])
def test_datagram_from_schema_dict(inp_dict, tf, datadir):
    ret = datagram_from_schema_path(inp_dict, datadir)
    print(ret)
    assert ret[0]["results"][0]["exists"] is tf


@pytest.mark.parametrize("inp_fn, l", [
    ("dummy_schema_1.json", 1),
    ("dummy_schema_2.json", 2)
])
def test_datagram_from_schema_file(inp_fn, l, datadir):
    ret = datagram_from_schema_file(inp_fn, datadir)
    print(json.dumps(ret, indent=1))
    assert isinstance(ret, Iterable) and len(ret) == l

