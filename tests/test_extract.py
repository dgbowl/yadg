import pytest
import os
from yadg.extractors import extract
import datatree
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "filetype, infile, outfile",
    [
        ("marda:biologic-mpr", "cp.mpr", "ref.cp.mpr.nc"),
        ("marda:biologic-mpt", "cp.mpt", "ref.cp.mpt.nc"),
        ("marda:agilent-ch", "hplc.CH", "ref.hplc.ch.nc"),
        ("marda:agilent-dx", "hplc.dx", "ref.hplc.dx.nc"),
        ("marda:phi-spe", "xps.spe", "ref.xps.spe.nc"),
        ("marda:panalytical-xrdml", "xrd.xrdml", "ref.xrd.xrdml.nc"),
    ],
)
def test_extract_marda(filetype, infile, outfile, datadir):
    os.chdir(datadir)
    ret = extract(filetype=filetype, path=infile)
    # ret.to_netcdf(outfile, engine="h5netcdf")
    ref = datatree.open_datatree(outfile)
    print(f"{ret=}")
    compare_datatrees(ret, ref)
