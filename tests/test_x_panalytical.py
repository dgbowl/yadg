import pytest
import os
import shutil
from yadg.extractors.panalytical.xrdml import extract as extract_xrdml
from yadg.extractors.panalytical.csv import extract as extract_csv
import xarray as xr


@pytest.fixture
def _datadir(tmpdir, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    base_dir, _ = os.path.split(test_dir)
    for ddir in ["test_x_panalytical_xrdml", "test_x_panalytical_csv"]:
        shutil.copytree(os.path.join(base_dir, ddir), str(tmpdir), dirs_exist_ok=True)
    return tmpdir


@pytest.mark.parametrize(
    "afile, bfile",
    [
        ("210520step1_30min.csv", "210520step1_30min.xrdml"),
    ],
)
def test_panalytical_consistency(afile, bfile, _datadir):
    os.chdir(_datadir)
    aret = extract_csv(fn=afile, encoding="utf-8", timezone="Europe/Berlin")
    bret = extract_xrdml(fn=bfile, encoding="utf-8", timezone="Europe/Berlin")
    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
