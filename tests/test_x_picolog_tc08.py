import pytest
import os
import pickle
from yadg.extractors.picolog.tc08 import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "20220723-porosity-study-15p-Cu-200mA-longrun-07.picolog",
        "20230917-16-S07-temperature.picolog",
    ],
)
def test_picolog_tc08(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
