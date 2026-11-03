import pytest
from yadg.extractors.ezchrom.asc import extract as extract_asc
from yadg.extractors.ezchrom.dat import extract as extract_dat
import xarray as xr
from pathlib import Path

DATA = Path(__file__).parent


@pytest.mark.parametrize(
    "dfile, afile",
    [
        ("2023-06-29-007.dat", "2023-06-29-007.dat.asc"),
        ("2023-06-29-014.dat", "2023-06-29-014.dat.asc"),
        ("230324.dat", "230324.dat.asc"),
    ],
)
def test_ezchrom_consistency(dfile, afile):
    aret = extract_dat(DATA / "test_x_ezchrom_dat" / dfile, timezone="Europe/Berlin")
    bret = extract_asc(
        DATA / "test_x_ezchrom_asc" / afile,
        timezone="Europe/Berlin",
        encoding="windows-1252",
    )
    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
