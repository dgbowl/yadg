import os

import pytest
import xarray as xr

from yadg.extractors.ezchrom.asc import extract as extract_asc
from yadg.extractors.ezchrom.dat import extract as extract_dat

from .utils import check_file


@pytest.mark.parametrize(
    "froot, locale",
    [
        ("2023-06-29-007", "en_US"),
        ("2023-06-29-014", "de_DE"),
        ("230324", "en_US"),
    ],
)
def test_eclab_consistency(froot, locale, datadir):
    os.chdir(datadir)
    kwargs = dict(timezone="Europe/Berlin", locale=locale, encoding="windows-1252")
    aret = check_file(f"{froot}.dat", kwargs, extract_dat)
    bret = check_file(f"{froot}.dat.asc", kwargs, extract_asc)

    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
