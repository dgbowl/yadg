import os
import json
import yaml
import yadg.core
import numpy as np
import pint
from typing import Union
from datatree import DataTree
import xarray as xr
from dgbowl_schemas.yadg import to_dataschema


def _schema_4_0(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = None
    else:
        raise ValueError()
    schema = {
        "metadata": {
            "provenance": "datagram_from_input",
            "schema_version": version,
            "timezone": input.get("timezone", "UTC"),
        },
        "steps": [
            {
                "parser": parser,
                "import": {
                    "prefix": input.get("prefix", ""),
                    "suffix": input.get("suffix", ""),
                    "contains": input.get("contains", ""),
                    "encoding": input.get("encoding", "utf-8"),
                    "folders": input.get("folders"),
                    "files": files,
                },
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    if "parameters" in input:
        schema["steps"][0]["parameters"] = input["parameters"]
    return schema


def _schema_4_1(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = input["folders"]
    else:
        raise ValueError()
    schema = {
        "metadata": {
            "provenance": {"type": "datagram_from_input"},
            "version": version,
            "timezone": input.get("timezone", "UTC"),
        },
        "steps": [
            {
                "parser": parser,
                "input": {
                    "prefix": input.get("prefix", None),
                    "suffix": input.get("suffix", None),
                    "contains": input.get("contains", None),
                    "encoding": input.get("encoding", "UTF-8"),
                    "files": files,
                },
                "parameters": input.get("parameters", None),
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    return schema


def _schema_4_2(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = input["folders"]
    else:
        raise ValueError()
    schema = {
        "metadata": {
            "provenance": {"type": "datagram_from_input"},
            "version": version,
            "timezone": input.get("timezone", "UTC"),
        },
        "steps": [
            {
                "parser": parser,
                "input": {
                    "prefix": input.get("prefix", None),
                    "suffix": input.get("suffix", None),
                    "contains": input.get("contains", None),
                    "encoding": input.get("encoding", "UTF-8"),
                    "files": files,
                },
                "parameters": input.get("parameters", None),
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    return schema


def _schema_5_0(input, parser, version):
    if "files" in input:
        files = input["files"]
    elif "case" in input:
        files = [input["case"]]
    elif "folders" in input:
        files = input["folders"]
    else:
        raise ValueError()

    if "filetype" in input:
        filetype = input.pop("filetype")
    elif "parameters" in input:
        filetype = input["parameters"].pop("filetype", None)
    else:
        filetype = None

    schema = {
        "metadata": {
            "provenance": {"type": "datagram_from_input"},
            "version": version,
        },
        "steps": [
            {
                "parser": parser,
                "input": {
                    "prefix": input.get("prefix", None),
                    "suffix": input.get("suffix", None),
                    "contains": input.get("contains", None),
                    "files": files,
                },
                "extractor": {
                    "filetype": filetype,
                    "timezone": input.get("timezone", "UTC"),
                    "locale": input.get("locale", "en_GB.UTF-8"),
                    "encoding": input.get("encoding", "UTF-8"),
                },
                "parameters": input.get("parameters", None),
                "externaldate": input.get("externaldate", None),
            }
        ],
    }
    return schema


def datagram_from_file(infile, datadir):
    os.chdir(datadir)
    with open(infile, "r") as f:
        if infile.endswith("json"):
            schema = json.load(f)
        else:
            schema = yaml.safe_load(f)
    ds = to_dataschema(**schema)
    return yadg.core.process_schema(ds)


def datagram_from_input(input, parser, datadir, version="4.0"):
    if version in {"4.0", "4.0.0", "4.0.1"}:
        schema = _schema_4_0(input, parser, version)
    elif version in {"4.1"}:
        schema = _schema_4_1(input, parser, version)
    elif version in {"4.2"}:
        schema = _schema_4_2(input, parser, version)
    elif version in {"5.0"}:
        schema = _schema_5_0(input, parser, version)
    os.chdir(datadir)
    ds = to_dataschema(**schema)
    return yadg.core.process_schema(ds)


def standard_datagram_test(datagram, testspec):
    assert len(datagram.children) == testspec["nsteps"], "wrong number of steps"
    if isinstance(testspec["step"], str):
        step = datagram[f"{testspec['step']}"]
    else:
        name = list(datagram.children.keys())[testspec["step"]]
        step = datagram[name]
    if len(step.children) > 0:
        for k, v in step.items():
            assert len(v["uts"]) == testspec["nrows"], (
                f"wrong number of timesteps in a child Dataset {k}: "
                f"ret: {len(v['uts'])}, ref: {testspec['nrows']}"
            )
    if "uts" in step:
        assert len(step["uts"]) == testspec["nrows"], (
            "wrong number of timesteps in a step: "
            f"ret: {len(step['uts'])}, ref: {testspec['nrows']}"
        )
    datagram.to_netcdf(".test.nc", engine="h5netcdf")


def pars_datagram_test(datagram, testspec, atol=0):
    if isinstance(testspec["step"], str):
        name = testspec["step"]
    else:
        name = list(datagram.children.keys())[testspec["step"]]
    step = datagram[name]
    for tk, tv in testspec["pars"].items():
        np.testing.assert_allclose(
            step[tk][testspec["point"]], tv["value"], equal_nan=True, atol=atol
        )
        if "unit" in tv:
            assert step[tk].attrs.get("units", None) == tv["unit"]
        if "sigma" in tv:
            sigmas = step[f"{tk}_std_err"]
            if sigmas.size == step[tk].size:
                sig = sigmas[testspec["point"]]
            else:
                sig = sigmas
            np.testing.assert_allclose(sig, tv["sigma"], equal_nan=True, atol=atol)
            # assert np.array_equal(sig, tv["sigma"], equal_nan=True)


def compare_result_dicts(result, reference, atol=1e-6):
    np.testing.assert_allclose(result["n"], reference["n"], atol=atol, equal_nan=True)
    np.testing.assert_allclose(result["s"], reference["s"], atol=atol, equal_nan=True)
    assert result["u"] == reference.get("u", None)


def dg_get_quantity(
    dt: DataTree,
    step: Union[str, int],
    col: str,
    utsrow: int = None,
) -> pint.Quantity:
    if isinstance(step, str):
        name = step
    else:
        name = list(dt.children.keys())[step]
    vals = dt[name].ds

    if utsrow is None:
        n = vals[col]
    else:
        n = vals.isel(uts=utsrow)[col]

    if f"{col}_std_err" not in vals:
        return n
    elif utsrow is None:
        d = vals[f"{col}_std_err"]
    else:
        d = vals.isel(uts=utsrow)[f"{col}_std_err"]

    u = vals[col].attrs.get("units", None)

    return {"n": n, "s": d, "u": u}


def compare_datatrees(ret: DataTree, ref: DataTree, atol: float = 1e-6):
    for k in ret:
        assert k in ref, f"Entry {k} not present in reference DataTree."
    for k in ref:
        assert k in ret, f"Entry {k} not present in result DataTree."

    for k in ret:
        if isinstance(ret[k], DataTree):
            compare_datatrees(ret[k], ref[k])
        elif isinstance(ret[k], (xr.Dataset, xr.DataArray)):
            xr.testing.assert_allclose(ret[k], ref[k], atol=atol)
        else:
            raise RuntimeError(f"Unknown entry '{k}' of type '{type(k)}'.")
