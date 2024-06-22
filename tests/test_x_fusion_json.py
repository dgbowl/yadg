import pytest
import os
import pickle
from yadg.extractors.fusion.json import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "15p-Cu-10mA-01 - Jun 08 2022, 16;10.fusion-data",
        "15p-Cu-10mA-01 - Jun 08 2022, 16;23.fusion-data",
        "AgPTFE28_100mA_NaS_01 - Aug 13 2021, 17;56.fusion-data",
        "AgPTFE28_100mA_NaS_01 - Aug 13 2021, 18;18.fusion-data",
    ],
)
def test_fusion_json(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf-8", timezone="Europe/Berlin")
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
