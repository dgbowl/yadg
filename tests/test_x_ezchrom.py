import os

import pytest
import xarray as xr

from yadg.extractors.ezchrom.asc import extract as extract_asc
from yadg.extractors.ezchrom.dat import extract as extract_dat

from .utils import check_file

KWARGS = dict(timezone="Europe/Berlin", encoding="windows-1252")


@pytest.mark.parametrize(
    "froot",
    [
        "2023-06-29-007",
        "2023-06-29-014",
        "230324",
    ],
)
def test_ezchrom_consistency(froot, datadir):
    os.chdir(datadir)

    aret = check_file(f"{froot}.dat", KWARGS, extract_dat)
    bret = check_file(f"{froot}.dat.asc", KWARGS, extract_asc)

    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
