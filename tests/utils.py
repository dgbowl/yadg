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
    toplevel=True,
    descend=True,
):
    for k in ret:
        assert k in ref, f"Entry {k} not present in reference DataTree."
    for k in ref:
        assert k in ret, f"Entry {k} not present in result DataTree."

    if toplevel and descend:
        assert ret.attrs == ref.attrs

    for k in ret:
        if isinstance(ret[k], DataTree):
            compare_datatrees(ret[k], ref[k], atol=atol, descend=descend)
        elif isinstance(ret[k], (xr.Dataset, xr.DataArray)):
            try:
                xr.testing.assert_allclose(ret[k], ref[k], atol=atol)
                assert ret[k].attrs == ref[k].attrs
            except AssertionError as e:
                e.args = (e.args[0] + f"Error happened on key: {k!r}\n",)
                raise e

        else:
            raise RuntimeError(f"Unknown entry '{k}' of type '{type(k)}'.")
