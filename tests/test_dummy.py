import pytest
import os
import json
import pytest
import yadg.core

from tests.utils import datadir
from tests.schemas import dummy_1, dummy_2, dummy_3, dummy_4, dummy_5
from tests.schemas import fail_1, fail_2, fail_3, fail_4, fail_5


@pytest.mark.parametrize(
    "inp_dict, l_dg, l_res",
    [
        (dummy_1, 1, 0),
        (dummy_2, 1, 1),
        (dummy_3, 1, 2),
        (dummy_4, 1, 2),
        (dummy_5, 1, 1),
    ],
)
def test_datagram_from_schema_dict(inp_dict, l_dg, l_res, datadir):
    os.chdir(datadir)
    assert yadg.core.validators.validate_schema(inp_dict), "invalid schema format"
    ret = yadg.core.process_schema(inp_dict)
    assert yadg.core.validators.validate_datagram(ret), "invalid datagram format"
    assert len(ret["steps"]) == l_dg, "wrong number of steps"
    if l_dg > 0:
        assert len(ret["steps"][0]["data"]) == l_res, "wrong number of timesteps"
    json.dumps(ret)


@pytest.mark.parametrize(
    "inp_fn, ts",
    [
        ("dummy_schema_1.json", {"nsteps": 1, "step": 0, "item": 0, "kwargs": {}}),
        (
            "dummy_schema_2.json",
            {"nsteps": 2, "step": 1, "item": 0, "kwargs": {"k": "v"}},
        ),
    ],
)
def test_datagram_from_schema_file(inp_fn, ts, datadir):
    os.chdir(datadir)
    jsonpath = datadir.join(inp_fn)
    with open(jsonpath, "r") as infile:
        schema = json.load(infile)
    assert yadg.core.validators.validate_schema(schema), "invalid schema format"
    ret = yadg.core.process_schema(schema)
    assert yadg.core.validators.validate_datagram(ret), "invalid datagram format"
    assert len(ret["steps"]) == ts["nsteps"], "wrong number of steps"
    assert (
        ret["steps"][ts["step"]]["data"][ts["item"]]["raw"] == ts["kwargs"]
    ), "kwargs not passed correctly"
    json.dumps(ret)


@pytest.mark.parametrize(
    "inp_dict, expr",
    [
        (fail_1, r"'parser'"),
        (fail_2, r"'dumm'"),
        (fail_3, r"2 were provided"),
        (fail_4, r"0 were provided"),
        (fail_5, r"'key'"),
    ],
)
def test_schema_validator(inp_dict, expr, datadir):
    os.chdir(datadir)
    with pytest.raises(AssertionError, match=expr):
        assert yadg.core.validators.validate_schema(inp_dict)
