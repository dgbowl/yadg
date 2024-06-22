import json
import yaml
import yadg.core
from datatree import DataTree
import xarray as xr
from dgbowl_schemas.yadg import to_dataschema


def datagram_from_file(infile):
    with open(infile, "r") as f:
        if infile.endswith("json"):
            schema = json.load(f)
        else:
            schema = yaml.safe_load(f)
    ds = to_dataschema(**schema)
    return yadg.core.process_schema(ds)


def compare_datatrees(
    ret: DataTree,
    ref: DataTree,
    atol: float = 1e-6,
    thislevel=False,
    descend=False,
):
    for k in ret:
        assert k in ref, f"Entry {k!r} not present in reference DataTree."
    for k in ref:
        assert k in ret, f"Entry {k!r} not present in result DataTree."

    if thislevel:
        check_attrs(ret.attrs, ref.attrs)

    for k in ret:
        if isinstance(ret[k], DataTree):
            compare_datatrees(
                ret[k], ref[k], atol=atol, thislevel=descend, descend=descend
            )
        elif isinstance(ret[k], (xr.Dataset, xr.DataArray)):
            try:
                xr.testing.assert_allclose(ret[k], ref[k], atol=atol)
            except AssertionError as e:
                e.args = (e.args[0] + f"Error happened on key: {k!r}\n",)
                raise AssertionError(*e.args)
            # if thislevel:
            #    check_attrs(ref.attrs, ret.attrs)
        else:
            raise RuntimeError(f"Unknown entry {k!r} of type {type(k)!r}.")


def check_attrs(ret: dict, ref: dict):
    for k in ret.keys():
        if k in {
            "yadg_process_date",
            "yadg_process_DataSchema",
            "yadg_extract_date",
            "yadg_version",
            "yadg_command",
        }:
            continue
        elif k.startswith("yadg_") or k in {
            "original_metadata",
            "fulldate",
        }:
            pass
        else:
            raise AssertionError(
                f"Metadata entry {k!r} is not allowed at this level of DataTree."
            )
        assert ret[k] == ref[k]
