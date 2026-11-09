import os
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from yadg.extractors.panalytical.csv import extract as extract_csv
from yadg.extractors.panalytical.xrdml import extract as extract_xrdml
from yadg.extractors.panalytical.xy import extract as extract_xy

from .utils import check_file

KWARGS = dict(timezone="Europe/Berlin", encoding="utf-8")

DATA = Path(__file__).parent


@pytest.mark.parametrize(
    "froot",
    [
        "210520step1_30min",
    ],
)
def test_panalytical_consistency(froot, datadir):
    os.chdir(datadir)
    aret = check_file(f"{froot}.csv", KWARGS, extract_csv)
    bret = check_file(f"{froot}.xrdml", KWARGS, extract_xrdml)
    cret = check_file(f"{froot}.xy", KWARGS, extract_xy)

    for key in aret.variables:
        if key.endswith("_uncertainty"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e

    for key in cret.variables:
        if key.endswith("_uncertainty"):
            continue
        try:
            np.testing.assert_allclose(cret[key].values, bret[key].values.ravel())
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
