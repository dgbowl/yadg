import json
import os
from distutils import dir_util

import pytest
from yadg import core

# Tests for the eclab module:
# TODO: Test parsers for different file versions.


@pytest.fixture
def datadir(tmpdir, request):
    """
    from: https://stackoverflow.com/a/29631801
    Fixture responsible for searching a folder with the same name of
    test module and, if available, moving all contents to a temporary
    directory so tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))
    return tmpdir


def datagram_from_eclab(input: dict, datadir: str):
    schema = {
        'metadata': {
            'provenance': "manual",
            'schema_version': "0.1",
        },
        'steps': {
            'parser': 'eclab',
            'import': {
                'files': [input['case']],
            },
        },
    }
    os.chdir(datadir)
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)


@pytest.mark.parametrize('input, ts', [
    ({'case': 'ca.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'ca.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'cp.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'cp.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'cv.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'cv.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'gcpl.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'gcpl.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'geis.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'geis.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'lsv.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'lsv.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'mb.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'mb.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'ocv.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'ocv.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'peis.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'peis.mpt'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
    ({'case': 'wait.mpr'},
    {'n_columns': 0, 'n_rows': 0, 'datapoint': 0, 'raw': {}}),
])
def test_datagram_from_eclab(input, ts, datadir):
    dg = datagram_from_eclab(input, datadir)
    assert core.validators.validate_datagram(dg)
    # TODO: Check column names
    # TODO: Check number of rows
    # TODO: Check loops
    # TODO: Check some settings
    # TODO: Check some data point values
    json.dumps(dg)
