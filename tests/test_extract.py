import pytest
import os
from yadg.extractors import extract
import xarray as xr
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "filetype, infile",
    [
        ("eclab.mpr", "cp.mpr"),
        ("eclab.mpt", "cp.mpt"),
        ("agilent.ch", "hplc.CH"),
        ("agilent.dx", "hplc.dx"),
        ("phi.spe", "xps.spe"),
        ("panalytical.xrdml", "xrd.xrdml"),
        ("touchstone.snp", "picovna.s1p"),
        ("ezchrom.asc", "230324.dat.asc"),
        ("ezchrom.dat", "230324.dat"),
        ("picolog.tc08", "20220723-porosity-study-15p-Cu-200mA-longrun-07.picolog"),
    ],
)
def test_yadg_extractors_extract_with_metadata(filetype, infile, datadir):
    os.chdir(datadir)
    outfile = f"{infile}.nc"
    ret = extract(
        filetype=filetype, path=infile, locale="en_GB", timezone="Europe/Berlin"
    )
    ret.to_netcdf(f"{outfile}.tmp", engine="h5netcdf")
    ref = xr.open_datatree(outfile, engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)
