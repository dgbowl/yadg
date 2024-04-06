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
    "filetype, infile, outfile",
    [
        ("touchstone.snp", "picovna.s1p", "ref.picovna.s1p.nc"),
        ("ezchrom.asc", "230324.dat.asc", "ref.230324.dat.asc.nc"),
        ("ezchrom.dat", "230324.dat", "ref.230324.dat.nc"),
    ],
)
def test_extract_yadg(filetype, infile, outfile, datadir):
    os.chdir(datadir)
    ret = extract(filetype=filetype, path=infile)
    # ret.to_netcdf(outfile, engine="h5netcdf")
    ref = datatree.open_datatree(outfile)
    print(f"{ret=}")
    compare_datatrees(ret, ref)
