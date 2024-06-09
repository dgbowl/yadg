import pytest
import os
from yadg.extractors import extract
import datatree
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "filetype, infile, outfile",
    [
        ("biologic-mpr", "cp.mpr", "ref.cp.mpr.nc"),
        ("biologic-mpt", "cp.mpt", "ref.cp.mpt.nc"),
        ("agilent-ch", "hplc.CH", "ref.hplc.ch.nc"),
        ("agilent-dx", "hplc.dx", "ref.hplc.dx.nc"),
        ("phi-spe", "xps.spe", "ref.xps.spe.nc"),
        ("panalytical-xrdml", "xrd.xrdml", "ref.xrd.xrdml.nc"),
    ],
)
def test_extract_marda(filetype, infile, outfile, datadir):
    os.chdir(datadir)
    ret = extract(filetype=filetype, path=infile)
    # ret.to_netcdf(outfile, engine="h5netcdf")
    ref = datatree.open_datatree(outfile)
    print(f"{ret=}")
    compare_datatrees(ret, ref)


@pytest.mark.parametrize(
    "filetype, infile",
    [
        ("touchstone.snp", "picovna.s1p"),
        ("ezchrom.asc", "230324.dat.asc"),
        ("ezchrom.dat", "230324.dat"),
        ("picolog.tc08", "20220723-porosity-study-15p-Cu-200mA-longrun-07.picolog"),
    ],
)
def test_extract_yadg(filetype, infile, datadir):
    os.chdir(datadir)
    outfile = f"ref.{infile}.nc"
    ret = extract(filetype=filetype, path=infile)
    # ret.to_netcdf(outfile, engine="h5netcdf")
    ref = datatree.open_datatree(outfile)
    print(f"{ret=}")
    compare_datatrees(ret, ref)
