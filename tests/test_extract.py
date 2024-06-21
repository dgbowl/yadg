import pytest
import os
from yadg.extractors import extract
import datatree
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "filetype, infile",
    [
        ("biologic-mpr", "cp.mpr"),
        ("biologic-mpt", "cp.mpt"),
        ("agilent-ch", "hplc.CH"),
        ("agilent-dx", "hplc.dx"),
        ("phi-spe", "xps.spe"),
        ("panalytical-xrdml", "xrd.xrdml"),
        ("touchstone.snp", "picovna.s1p"),
        ("ezchrom.asc", "230324.dat.asc"),
        ("ezchrom.dat", "230324.dat"),
        ("picolog.tc08", "20220723-porosity-study-15p-Cu-200mA-longrun-07.picolog"),
    ],
)
def test_yadg_extractors_extract_with_metadata(filetype, infile, datadir):
    os.chdir(datadir)
    outfile = f"{infile}.nc"
    ret = extract(filetype=filetype, path=infile)
    # ret.to_netcdf(outfile, engine="h5netcdf")
    ref = datatree.open_datatree(outfile, engine="h5netcdf")
    print(f"{ret=}")
    assert ret.attrs.keys() == ref.attrs.keys()
    # let's delete metadata we know will be wrong
    for k in {
        "yadg_extract_date",
        "yadg_version",
        "yadg_command",
    }:
        del ret.attrs[k]
        del ref.attrs[k]
    compare_datatrees(ret, ref, toplevel=True, descend=True)
