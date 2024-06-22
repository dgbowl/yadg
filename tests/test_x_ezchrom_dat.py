import pytest
import os
import pickle
from yadg.extractors.ezchrom.dat import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "2023-06-29-007.dat",
        "2023-06-29-014.dat",
        "230324.dat",
    ],
)
def test_ezchrom_dat(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
