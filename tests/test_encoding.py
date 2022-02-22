import pytest
from tests.utils import datagram_from_input, standard_datagram_test


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts1 - BOM requires utf-8-sig encoding
                "case": "log 2021-09-17 11-26-14.140.csv",
                "parser": "basiccsv",
                "encoding": "utf-8-sig",
                "parameters": {
                    "timestamp": {
                        "timestamp": {"index": 0, "format": '"%Y-%m-%d %H:%M:%S.%f"'}
                    },
                    "units": {},
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 239,
                "point": 0,
                "pars": {"uts": {"value": 1631877974.045}},
                "errortype": ValueError,
                "errorexpr": "ufeff",
            },
        ),
    ],
)
def test_datagram(input, ts, datadir):
    ret = datagram_from_input(input, input["parser"], datadir)
    standard_datagram_test(ret, ts)

    fail_input = input.copy()
    del fail_input["encoding"]
    with pytest.raises(ts["errortype"], match=ts["errorexpr"]):
        datagram_from_input(fail_input, fail_input["parser"], datadir)
