import pytest
import os
import pickle
from pathlib import Path
from yadg.extractors.agilent.ch import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "extracted-3487d194-9155-4f79-8f11-dbd18ce53187.CH",
    ],
)
def test_agilent_ch(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True)
