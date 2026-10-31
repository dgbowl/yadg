import pytest
from yadg.extractors.panalytical.xrdml import extract as extract_xrdml
from yadg.extractors.panalytical.csv import extract as extract_csv
import xarray as xr
from pathlib import Path

DATA = Path(__file__).parent


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("210520step1_30min.csv", "210520step1_30min.xrdml"),
    ],
)
def test_panalytical_consistency(afile, bfile):
    aret = extract_csv(
        DATA / "test_x_panalytical_csv" / afile,
        encoding="utf-8",
        timezone="Europe/Berlin",
    )
    bret = extract_xrdml(
        DATA / "test_x_panalytical_xrdml" / bfile,
        encoding="utf-8",
        timezone="Europe/Berlin",
    )
    for key in aret.variables:
        if key.endswith("_uncertainty"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
