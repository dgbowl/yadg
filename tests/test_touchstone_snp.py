import pytest
import os
import pickle
from yadg.extractors.touchstone.snp import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile",
    [
        "picovna.s1p",
        "Device_r_40um.s1p",
        "Device_r_60um.s1p",
        "Fig8_0.6cm.s1p",
        "Fig8_5.6cm.s1p",
        "SCENARIO1_pulserside_30k_3G.s1p",
        "SCENARIO4_pulserside_30k_3G.s1p",
        "CABLE_3_5MM_1N_TYPE_CONNECTORS.S2P",
        "VNA_radial_middle.s1p",
        "VNA_radial_middle.s2p",
    ],
)
def test_touchstone_snp(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf-8", timezone="Europe/Berlin")
    outfile = f"ref.{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out)
    compare_datatrees(ret, ref)
