import pytest
import os
import numpy as np
from distutils import dir_util
from yadg.extractors.ezchrom.asc import extract as extract_asc
from yadg.extractors.ezchrom.dat import extract as extract_dat


@pytest.fixture
def ezchrom_datadir(tmpdir, request):
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    base_dir, _ = os.path.split(test_dir)
    for ddir in ["test_ezchrom_dat", "test_ezchrom_asc"]:
        dir_util.copy_tree(os.path.join(base_dir, ddir), str(tmpdir))
    return tmpdir


@pytest.mark.parametrize(
    "datfile, ascfile",
    [
        ("2023-06-29-007.dat", "2023-06-29-007.dat.asc"),
        ("2023-06-29-014.dat", "2023-06-29-014.dat.asc"),
        ("230324.dat", "230324.dat.asc"),
    ],
)
def test_ezchrom_consistency(datfile, ascfile, ezchrom_datadir):
    os.chdir(ezchrom_datadir)
    dat = extract_dat(fn=datfile, timezone="Europe/Berlin")
    asc = extract_asc(fn=ascfile, timezone="Europe/Berlin", encoding="windows-1252")
    for d, a in zip(dat.values(), asc.values()):
        for key in d.variables:
            np.testing.assert_allclose(d[key], a[key], rtol=1e-4)
            assert d[key].attrs == a[key].attrs
