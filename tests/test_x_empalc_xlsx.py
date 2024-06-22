import pytest
import os
import pickle
from yadg.extractors.empalc.xlsx import extract
from .utils import compare_datatrees, datagram_from_file


@pytest.mark.parametrize(
    "infile",
    [
        "Cu-25p_v2.xlsx",
        "samplename_newlines.xlsx",
        "2022-09-12-15-37-07+0200_spCuDurapore05_old_injections_LC-data.xlsx",
    ],
)
def test_empalc_xlsx(infile, datadir):
    os.chdir(datadir)
    ret = extract(fn=infile)
    outfile = f"{infile}.pkl"
    with open(outfile, "rb") as inp:
        ref = pickle.load(inp)
    print(f"{ret=}")
    with open(outfile, "wb") as out:
        pickle.dump(ret, out, 5)
    compare_datatrees(ret, ref, thislevel=True)


def test_empalc_lock_stock_dataschema(datadir):
    os.chdir(datadir)
    ret = datagram_from_file("lock_stock_dataschema.yml")
    print(f"{ret=}")
    for k in {"height", "concentration", "retention time", "area"}:
        assert ret["LC"][k].shape == (7, 2)
