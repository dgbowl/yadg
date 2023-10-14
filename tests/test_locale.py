import pytest
from tests.utils import (
    datagram_from_input,
    compare_datatrees,
)
from datatree import open_datatree


@pytest.mark.parametrize(
    "input",
    [
        {  # ts0
            "case": "sheet.UK.tsv",
            "locale": "en_GB.UTF-8",
            "filetype": "None",
            "parameters": {
                "sep": "\t",
                "timestamp": {
                    "date": {"index": 0, "format": "%d/%m/%Y"},
                    "time": {"index": 1, "format": "%H:%M:%S"},
                },
            },
        },
        {  # ts1
            "case": "sheet.DE.tsv",
            "locale": "de_DE.UTF-8",
            "filetype": "None",
            "parameters": {
                "sep": "\t",
                "timestamp": {
                    "date": {"index": 0, "format": "%d.%m.%Y"},
                    "time": {"index": 1, "format": "%H:%M:%S"},
                },
            },
        },
        {  # ts2
            "case": "sheet.US.tsv",
            "locale": "en_US.UTF-8",
            "filetype": "None",
            "parameters": {
                "sep": "\t",
                "timestamp": {
                    "date": {"index": 0, "format": "%m/%d/%Y"},
                    "time": {"index": 1, "format": "%H:%M:%S %p"},
                },
            },
        },
    ],
)
def test_locale_from_basiccsv(input, datadir):
    ret = datagram_from_input(input, "basiccsv", datadir, version="5.0")
    # ret.to_netcdf("ref.sheet.nc")
    print(f"{ret=}")
    ref = open_datatree("ref.sheet.nc")
    compare_datatrees(ret, ref)
