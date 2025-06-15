import pytest
import os
import shutil
from yadg.extractors.ezchrom.asc import extract as extract_asc
from yadg.extractors.ezchrom.dat import extract as extract_dat
import xarray as xr
from pathlib import Path


@pytest.fixture
def ezchrom_datadir(tmpdir, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    base_dir, _ = os.path.split(test_dir)
    for ddir in ["test_x_ezchrom_dat", "test_x_ezchrom_asc"]:
        shutil.copytree(os.path.join(base_dir, ddir), str(tmpdir), dirs_exist_ok=True)
    return tmpdir


@pytest.mark.parametrize(
    "dfile, afile",
    [
        ("2023-06-29-007.dat", "2023-06-29-007.dat.asc"),
        ("2023-06-29-014.dat", "2023-06-29-014.dat.asc"),
        ("230324.dat", "230324.dat.asc"),
    ],
)
def test_ezchrom_consistency(dfile, afile, ezchrom_datadir):
    os.chdir(ezchrom_datadir)
    aret = extract_dat(
        source=Path(dfile),
        timezone="Europe/Berlin",
    )
    bret = extract_asc(
        source=Path(afile),
        timezone="Europe/Berlin",
        encoding="windows-1252",
    )
    for key in aret.variables:
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
