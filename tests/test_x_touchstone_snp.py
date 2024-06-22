import pytest
import os
import pickle
from yadg.extractors.touchstone.snp import extract
from .utils import compare_datatrees


@pytest.mark.parametrize(
    "infile, locale",
    [
        ("picovna.s1p", "en_GB"),
        ("Device_r_40um.s1p", "en_GB"),
        ("Device_r_60um.s1p", "en_GB"),
        ("Fig8_0.6cm.s1p", "en_GB"),
        ("Fig8_5.6cm.s1p", "en_GB"),
        ("SCENARIO1_pulserside_30k_3G.s1p", "en_GB"),
        ("SCENARIO4_pulserside_30k_3G.s1p", "en_GB"),
        ("CABLE_3_5MM_1N_TYPE_CONNECTORS.S2P", "en_GB"),
        ("VNA_radial_middle.s1p", "en_GB"),
        ("VNA_radial_middle.s2p", "en_GB"),
        ("2024-06-20-01-empty.s1p", "de_DE"),
    ],
)
def test_touchstone_snp(infile, locale, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile, encoding="utf-8", timezone="Europe/Berlin", locale=locale)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)
