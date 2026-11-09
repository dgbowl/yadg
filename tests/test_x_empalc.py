import os

import pytest
import xarray as xr

from yadg.extractors.empalc.csv import extract as extract_csv
from yadg.extractors.empalc.xlsx import extract as extract_xls

from .utils import check_file, datagram_from_file

KWARGS = dict(timezone="Europe/Berlin", encoding="utf-8")


@pytest.mark.parametrize(
    "froot",
    [
        "Cu-25p_v2",
    ],
)
def test_empalc_consistency(froot, datadir):
    os.chdir(datadir)
    aret = check_file(f"{froot}.xlsx", KWARGS, extract_xls)
    bret = check_file(f"{froot}.csv", KWARGS, extract_csv)

    for key in aret.variables:
        if key.endswith("_uncertainty"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e


@pytest.mark.parametrize(
    "infile",
    [
        "Cu-20p_v2.csv",
    ],
)
def test_empalc_csv(infile, datadir):
    os.chdir(datadir)
    check_file(infile, KWARGS, extract_csv)


@pytest.mark.parametrize(
    "infile",
    [
        "samplename_newlines.xlsx",
        "2022-09-12-15-37-07+0200_spCuDurapore05_old_injections_LC-data.xlsx",
    ],
)
def test_empalc_xlsx(infile, datadir):
    os.chdir(datadir)
    check_file(infile, KWARGS, extract_xls)


def test_empalc_lock_stock_dataschema(datadir):
    os.chdir(datadir)
    ret = datagram_from_file("lock_stock_dataschema.yml")
    print(f"{ret=}")
    for k in {"height", "concentration", "retention time", "area"}:
        assert ret["LC"][k].shape == (7, 2)
