import pytest
import os
import xarray as xr
from pathlib import Path
from yadg.extractors import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "filetype, infile",
    [
        ("fusion.json", "20220608-porosity-study-15p-Cu-10mA-GC.zip"),
    ],
)
def test_yadg_extract_from_zip(filetype, infile, datadir):
    os.chdir(datadir)
    ret = extract(
        filetype=filetype, path=Path(infile), locale="en_GB", timezone="Europe/Berlin"
    )
    outfile = f"{infile}.nc"
    ret.to_netcdf(f"{outfile}.tmp", engine="h5netcdf")
    ref = xr.open_datatree(outfile, engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)
