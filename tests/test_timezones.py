import os
from .utils import datagram_from_file


def test_timestamp_parsing(datadir):
    os.chdir(datadir)
    utc = datagram_from_file("ssv_utc.json")
    cet = datagram_from_file("ssv_cet.json")
    diff = utc["0"].uts.to_numpy() - cet["0"].uts.to_numpy()
    assert diff[0] == 7200, "CEST should be 2 hours ahead of UTC"
    assert diff[1] == 7200, "CEST should be 2 hours ahead of UTC"
    assert diff[2] == 3600, "CET should be 1 hours ahead of UTC"


def test_uts_parsing(datadir):
    os.chdir(datadir)
    utc = datagram_from_file("csv_utc.json")
    cet = datagram_from_file("csv_cet.json")
    diff = utc["0"].uts.to_numpy() - cet["0"].uts.to_numpy()
    assert (diff == 0).all(), "'uts' column parsing should ignore timezones"


def test_isotimestamp_parsing(datadir):
    os.chdir(datadir)
    utc = datagram_from_file("csv_utc.json")
    cet = datagram_from_file("csv_cet.json")
    diff = utc["0"].uts.to_numpy() - cet["0"].uts.to_numpy()
    assert (diff == 0).all(), "Z-suffix should override timezone provided in schema"


def test_isotimestamp_parsing_utc(datadir):
    os.chdir(datadir)
    dg = datagram_from_file("iso_utc.json")

    assert dg["0"].uts[0] == 1622557825.0, "Z-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[1] == 1622557825.0 + 7200 + 1
    ), "±HH:MM-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[2] == 1622557825.0 + 2
    ), "no suffix with timezone = UTC parsed to 'uts' correctly"


def test_isotimestamp_parsing_cet(datadir):
    os.chdir(datadir)
    dg = datagram_from_file("iso_cet.json")
    assert dg["0"].uts[0] == 1622557825.0, "Z-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[1] == 1622557825.0 + 7200 + 1
    ), "±HH:MM-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[2] == 1622557825.0 - 7200 + 2
    ), "no suffix with timezone = CEST parsed to 'uts' correctly"
