import pytest
import os
import pickle
from yadg.extractors.empalc.csv import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "Cu-20p_v2.csv",
        "Cu-25p_v2.csv",
    ],
)
def test_empalc_csv(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf-8")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
