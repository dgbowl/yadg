import pytest
import os
import pickle
from yadg.extractors.drycal.txt import extract
import xarray as xr


@pytest.mark.parametrize(
    "infile",
    [
        "20211011_DryCal_out.txt",
    ],
)
def test_drycal_txt(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf8", timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    xr.testing.assert_identical(ret, ref)
