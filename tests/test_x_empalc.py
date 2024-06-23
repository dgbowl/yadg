import pytest
import os
import shutil
from yadg.extractors.empalc.xlsx import extract as extract_xls
from yadg.extractors.empalc.csv import extract as extract_csv
import xarray as xr


@pytest.fixture
def _datadir(tmpdir, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    base_dir, _ = os.path.split(test_dir)
    for ddir in ["test_x_empalc_xlsx", "test_x_empalc_csv"]:
        shutil.copytree(os.path.join(base_dir, ddir), str(tmpdir), dirs_exist_ok=True)
    return tmpdir


@pytest.mark.parametrize(
    "afile, bfile",
    [("Cu-25p_v2.xlsx", "Cu-25p_v2.csv")],
)
def test_empalc_consistency(afile, bfile, _datadir):
    os.chdir(_datadir)
    aret = extract_xls(fn=afile)
    bret = extract_csv(fn=bfile, encoding="utf-8")

    for key in aret.variables:
        if key.endswith("std_err"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
