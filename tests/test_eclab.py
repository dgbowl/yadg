import pytest
import os
import json
from distutils import dir_util

from yadg import core

# Tests for the eclab module:
# TODO:


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
    pass


def datagram_from_schema_dict(schema):
    pass


@pytest.mark.parametrize("inp_dict, l_dg, l_res", [])
def test_datagram_from_schema_dict(inp_dict, l_dg, l_res, datadir):
    pass


@pytest.mark.parametrize("inp_fn, ts", [])
def test_datagram_from_schema_file(inp_fn, ts, datadir):
    pass


@pytest.mark.parametrize("inp_dict, expr", [])
def test_schema_validator(inp_dict, expr, datadir):
    pass
