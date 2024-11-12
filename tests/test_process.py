import pytest
import os
import json
import yadg.dgutils
import yadg.core
import xarray as xr
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "input",
    [
        "test_locale_passthrough.json",
    ],
)
def test_process_locale_passthrough(input, datadir):
    os.chdir(datadir)

    with open(f"{input}") as infile:
        obj = json.load(infile)

    schema = yadg.dgutils.update_schema(obj)
    ret = yadg.core.process_schema(schema)
    # ret.to_netcdf(f"{input}.nc", engine="h5netcdf")
    ref = xr.open_datatree(f"{input}.nc", engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)
