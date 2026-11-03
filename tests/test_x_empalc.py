import pytest
from yadg.extractors.empalc.xlsx import extract as extract_xls
from yadg.extractors.empalc.csv import extract as extract_csv
import xarray as xr
from pathlib import Path

DATA = Path(__file__).parent


@pytest.mark.parametrize(
    "afile, bfile",
    [("Cu-25p_v2.xlsx", "Cu-25p_v2.csv")],
)
def test_empalc_consistency(afile, bfile):
    aret = extract_xls(DATA / "test_x_empalc_xlsx" / afile)
    bret = extract_csv(DATA / "test_x_empalc_csv" / bfile, encoding="utf-8")

    for key in aret.variables:
        if key.endswith("_uncertainty"):
            continue
        try:
            xr.testing.assert_allclose(aret[key], bret[key])
        except AssertionError as e:
            e.args = (e.args[0] + f"Error happened on key: {key!r}\n",)
            raise e
