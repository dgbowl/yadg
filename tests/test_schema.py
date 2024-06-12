import pytest
import os
import datatree
import yadg.core
from dgbowl_schemas.yadg import to_dataschema, DataSchema_4_0, DataSchema_4_1
from pydantic import ValidationError
from pydantic.v1 import ValidationError as ValidationError_v1
from .utils import datagram_from_file

ts0 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "suffix": "wrong"}}],
}
ts1 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"files": ["ts1.dummy.json"]}}],
}
ts2 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "contains": ".dummy."}}],
}
ts3 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["ts0.dummy.json", "ts1.dummy.json"]},
        }
    ],
}
ts4 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"folders": ["."], "prefix": "ts", "contains": "1"},
        }
    ],
}
fts0 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parse": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts1 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dumm",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts2 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {
                "files": ["dummy_schema_1.json", "dummy_schema_2.json"],
                "folders": ["."],
            },
        }
    ],
}
fts3 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {}}],
}
fts4 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
            "key": "value",
        }
    ],
}

ts5 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "input": {
                "folders": ["."],
                "suffix": "json",
                "contains": "schema",
                "exclude": "3.1.0",
            },
            "parameters": {},
        }
    ],
}

fts5 = {
    "metadata": {"provenance": "wrong", "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts6 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.0"},
    "steps": [
        {
            "parser": "dummy",
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts7 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts8 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
            "parameters": {"k": "v"},
        }
    ],
}


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
    print(f"{ret=}")
    assert len(ret.children) == l_dg, "wrong number of steps"
    if l_dg > 0:
        assert len(ret["0"].get("uts", [])) == l_res, "wrong number of timesteps"
    ret.to_netcdf("test.nc", engine="h5netcdf")
    ref = datatree.open_datatree("test.nc", engine="h5netcdf")
    print(ref)
    assert ref == ret


@pytest.mark.parametrize(
    "inp_fn, ts",
    [
        (
            "ts0.dummy.json",
            {"nsteps": 1, "step": "0", "item": 0, "kwargs": {}},
        ),
        (
            "ts1.dummy.json",
            {"nsteps": 2, "step": "1", "item": 0, "kwargs": {"k": "v"}},
        ),
        (
            "ts2.json",
            {"nsteps": 2, "step": "1", "item": 0, "kwargs": {"k": "v"}},
        ),
    ],
)
def test_datagram_from_schema_file(inp_fn, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_file(inp_fn)
    assert len(ret.children) == ts["nsteps"], (
        "wrong number of steps: " f"got: {len(ret.children)}, expected: {ts['nsteps']}"
    )
    for k, v in ts["kwargs"].items():
        assert ret[ts["step"]][k][ts["item"]] == v, "kwargs not passed correctly"
    ret.to_netcdf("test.nc", engine="h5netcdf")
    ref = datatree.open_datatree("test.nc", engine="h5netcdf")
    print(ref)
    assert ref == ret


@pytest.mark.parametrize(
    "inp_dict, expr",
    [
        (fts0, r"Discriminator 'parser' is missing in value"),
        (fts1, r"No match for discriminator 'parser' and value 'dumm'"),
        (fts2, r"Both 'files' and 'folders'"),
        (fts3, r"Neither 'files' nor 'folders'"),
        (fts4, r"steps -> 0 -> Dummy -> key\n  extra fields not permitted"),
    ],
)
def test_schema_validator_4_0(inp_dict, expr, datadir):
    os.chdir(datadir)
    with pytest.raises((ValidationError, ValidationError_v1), match=expr):
        assert DataSchema_4_0(**inp_dict)


@pytest.mark.parametrize(
    "inp_dict, expr",
    [
        (fts5, r"metadata -> provenance\n  value is not a valid dict"),
        (fts6, r"metadata -> version\n  unexpected value"),
        (fts7, r"steps -> 0 -> Dummy -> input\n  field required"),
        (fts8, r"Discriminator 'parser' is missing in value"),
    ],
)
def test_schema_validator_4_1(inp_dict, expr, datadir):
    os.chdir(datadir)
    with pytest.raises((ValidationError, ValidationError_v1), match=expr):
        assert DataSchema_4_1(**inp_dict)
