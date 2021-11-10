import pytest

from tests.utils import (compare_result_dicts, datadir, datagram_from_input,
                         pars_datagram_test, standard_datagram_test)

# Tests for the eclab module:
# TODO: Test parsers for different file versions.


@pytest.mark.parametrize(
    'input, ts',
    [
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
        (
            {
                'case': 'ca.mpr'
            },
            {
                'nsteps': 0,
                'steps': 0,
                'nrows': 0,
                'point': 0,
                'pars': {}
            },
        ),
    ],
)
def test_datagram_from_eclab(input, ts, datadir):
    ret = datagram_from_input(input, "eclab", datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)
