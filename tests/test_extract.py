import pytest
import os
from yadg.extractors import extract
import datatree
import numpy as np


@pytest.mark.parametrize(
    "filetype, infile, outfile",
    [
        ("marda:biologic-mpr", "cp.mpr", "ref.cp.mpr.nc"),
        ("marda:biologic-mpt", "cp.mpt", "ref.cp.mpt.nc"),
    ],
)
def test_extract_marda(filetype, infile, outfile, datadir):
    os.chdir(datadir)
    ret = extract(filetype=filetype, path=infile)
    print(f"{ret=}")
    ref = datatree.open_datatree(outfile)
    # ret.to_netcdf("test.nc", engine="h5netcdf")
    print(f"{ref=}")
    for k in ret:
        if "units" in ret[k].attrs:
            np.testing.assert_allclose(ret[k], ref[k])
        else:
            np.testing.assert_array_equal(ret[k], ref[k])
    for k in ref:
        assert k in ret
