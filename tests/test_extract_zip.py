import pytest
import os
import xarray as xr
from pathlib import Path
from yadg.extractors import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "filetype, infile, ignore, suffix",
    [
        ("fusion.json", "fusion-json.zip", False, None),
        ("ezchrom.asc", "ezchrom-asc.zip", False, None),
        ("ezchrom.asc", "ezchrom-txt.zip", False, ".txt"),
        ("eclab.mpr", "eclab-mpr.zip", True, None),
    ],
)
def test_extract_from_zip(filetype, infile, ignore, suffix, datadir):
    os.chdir(datadir)
    ret = extract(
        filetype=filetype,
        path=Path(infile),
        locale="en_GB",
        timezone="Europe/Berlin",
        ignore_merge_errors=ignore,
        suffix=suffix,
    )
    outfile = f"{infile}.nc"
    ret.to_netcdf(f"{outfile}.tmp", engine="h5netcdf")
    ref = xr.open_datatree(outfile, engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)
