import pytest
import os
import json
from distutils import dir_util

from yadg import core

@pytest.fixture
def datadir(tmpdir, request):
    """
    from: https://stackoverflow.com/a/29631801
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)
    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))
    return tmpdir

def datagram_from(fn, datadir):
    os.chdir(datadir)
    with open(fn, "r") as infile:
        schema = json.load(infile)
    assert core.validators.validate_schema(schema)
    return core.process_schema(schema)

def test_timestamp_parsing(datadir):
    utc = datagram_from("ssv_utc.json", datadir)
    assert core.validators.validate_datagram(utc)
    cet = datagram_from("ssv_cet.json", datadir)
    assert core.validators.validate_datagram(cet)
    assert utc["data"][0]["timesteps"][0]["uts"] - cet["data"][0]["timesteps"][0]["uts"] == 7200
    assert utc["data"][0]["timesteps"][1]["uts"] - cet["data"][0]["timesteps"][1]["uts"] == 3600

def test_uts_parsing(datadir):
    utc = datagram_from("csv_utc.json", datadir)
    assert core.validators.validate_datagram(utc)
    cet = datagram_from("csv_cet.json", datadir)
    assert core.validators.validate_datagram(cet)
    assert utc["data"][0]["timesteps"][0]["uts"] - cet["data"][0]["timesteps"][0]["uts"] == 0
    assert utc["data"][0]["timesteps"][1]["uts"] - cet["data"][0]["timesteps"][1]["uts"] == 0

def test_isotimestamp_parsing(datadir):
    utc = datagram_from("csv_utc.json", datadir)
    assert core.validators.validate_datagram(utc)
    cet = datagram_from("csv_cet.json", datadir)
    assert core.validators.validate_datagram(cet)
    assert utc["data"][0]["timesteps"][0]["uts"] - cet["data"][0]["timesteps"][0]["uts"] == 0
    assert utc["data"][0]["timesteps"][1]["uts"] - cet["data"][0]["timesteps"][1]["uts"] == 0

def test_isotimestamp_parsing_utc(datadir):
    dg = datagram_from("iso_utc.json", datadir)
    assert core.validators.validate_datagram(dg)
    assert dg["data"][0]["timesteps"][0]["uts"] == 1622557825.0
    assert dg["data"][0]["timesteps"][1]["uts"] == 1622557825.0 + 7200 + 1
    assert dg["data"][0]["timesteps"][2]["uts"] == 1622557825.0 + 2

def test_isotimestamp_parsing_cet(datadir):
    dg = datagram_from("iso_cet.json", datadir)
    assert core.validators.validate_datagram(dg)
    assert dg["data"][0]["timesteps"][0]["uts"] == 1622557825.0
    assert dg["data"][0]["timesteps"][1]["uts"] == 1622557825.0 + 7200 + 1
    assert dg["data"][0]["timesteps"][2]["uts"] == 1622557825.0 - 7200 + 2