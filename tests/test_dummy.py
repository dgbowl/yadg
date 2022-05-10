import pytest
import os
import json
import yadg.core
from dgbowl_schemas.yadg import to_dataschema, DataSchema_4_0, DataSchema_4_1
from pydantic import ValidationError

from .schemas import ts0, ts1, ts2, ts3, ts4, ts5
from .schemas import fts0, fts1, fts2, fts3, fts4, fts5, fts6, fts7, fts8

from .utils import datagram_from_file, standard_datagram_test, pars_datagram_test

@pytest.mark.parametrize(
    "inp_dict, l_dg, l_res",
    [
        (ts0, 1, 0),
        (ts1, 1, 1),
        (ts2, 1, 2),
        (ts3, 1, 2),
        (ts4, 1, 1),
        (ts5, 1, 0),
    ],
)
def test_datagram_from_schema_dict(inp_dict, l_dg, l_res, datadir):
    os.chdir(datadir)
    ds = to_dataschema(**inp_dict)
    ret = yadg.core.process_schema(ds)
    print(ret)
    assert yadg.core.validators.validate_datagram(ret), "invalid datagram format"
    assert len(ret["steps"]) == l_dg, "wrong number of steps"
    if l_dg > 0:
        assert len(ret["steps"][0]["data"]) == l_res, "wrong number of timesteps"
    json.dumps(ret)


@pytest.mark.parametrize(
    "inp_fn, ts",
    [
        (
            "ts0.dummy.json",
            {"nsteps": 1, "step": 0, "item": 0, "kwargs": {}},
        ),
        (
            "ts1.dummy.json",
            {"nsteps": 2, "step": 1, "item": 0, "kwargs": {"k": "v"}},
        ),
        (
            "ts2.json",
            {"nsteps": 2, "step": 1, "item": 0, "kwargs": {"k": "v"}},
        ),
    ],
)
def test_datagram_from_schema_file(inp_fn, ts, datadir):
    os.chdir(datadir)
    jsonpath = datadir.join(inp_fn)
    with open(jsonpath, "r") as infile:
        schema = json.load(infile)
    ds = to_dataschema(**schema)
    ret = yadg.core.process_schema(ds)
    assert yadg.core.validators.validate_datagram(ret), "invalid datagram format"
    assert len(ret["steps"]) == ts["nsteps"], "wrong number of steps"
    assert (
        ret["steps"][ts["step"]]["data"][ts["item"]]["raw"] == ts["kwargs"]
    ), "kwargs not passed correctly"
    json.dumps(ret)


@pytest.mark.parametrize(
    "inp_dict, expr",
    [
        (fts0, r"parser"),
        (fts1, r"given=dumm"),
        (fts2, r"Both 'files' and 'folders'"),
        (fts3, r"Neither 'files' nor 'folders'"),
        (fts4, r"extra fields not permitted"),
    ],
)
def test_schema_validator_4_0(inp_dict, expr, datadir):
    os.chdir(datadir)
    with pytest.raises(ValidationError, match=expr):
        assert DataSchema_4_0(**inp_dict)


@pytest.mark.parametrize(
    "inp_dict, expr",
    [
        (fts5, r"metadata -> provenance"),
        (fts6, r"metadata -> version"),
        (fts7, r"steps -> 0 -> input"),
        (fts8, r"steps -> 0 -> parser"),
    ],
)
def test_schema_validator_4_1(inp_dict, expr, datadir):
    os.chdir(datadir)
    with pytest.raises(ValidationError, match=expr):
        assert DataSchema_4_1(**inp_dict)


@pytest.mark.parametrize(
    "infile, ts",
    [
        (
            "ts0_dummy_tomato.yml",
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 20,
                "point": 9,
                "pars": {
                    "uts": {"value": 100000000.905299},
                    "value": {"value": 0.485624320335729, "sigma": 0.0, "unit": " "},
                },
            },
        ),
    ],
)
def test_dummy_tomato(infile, ts, datadir):
    ret = datagram_from_file(infile, datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)