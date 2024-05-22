import pytest
from tests.utils import (
    datagram_from_file,
    pars_datagram_test,
    standard_datagram_test,
)


@pytest.mark.parametrize(
    "infile, ts",
    [
        (
            "ts0_electrochem_tomato.yml",
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 51,
                "point": 9,
                "pars": {
                    "uts": {"value": 1650490355.3152814},
                    "Ewe": {"value": 4.2000856399, "sigma": 0.00015, "unit": "V"},
                    "I": {"value": 0.0044998624, "sigma": 4e-7, "unit": "A"},
                },
            },
        ),
    ],
)
def test_electrochem_tomato(infile, ts, datadir):
    ret = datagram_from_file(infile, datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)
