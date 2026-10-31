import pytest
import os
import pickle
from yadg.extractors.panalytical.xrdml import extract
from .utils import compare_datatrees
from pathlib import Path


@pytest.mark.parametrize(
    "infile",
    [
        "210520step1_30min.xrdml",
    ],
)
def test_panalytical_xrdml(infile, datadir):
    os.chdir(datadir)
    ret = extract(Path(infile), timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    compare_datatrees(ret, ref, thislevel=True)
