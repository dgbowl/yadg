import os
import json
from dgbowl_schemas.yadg import to_dataschema
import yadg.core


def datagram_from(fn, datadir):
    os.chdir(datadir)
    with open(fn, "r") as infile:
        schema = json.load(infile)
    ds = to_dataschema(**schema)
    return yadg.core.process_schema(ds)


def test_timestamp_parsing(datadir):
    utc = datagram_from("ssv_utc.json", datadir)
    cet = datagram_from("ssv_cet.json", datadir)
    diff = utc["0"].uts.to_numpy() - cet["0"].uts.to_numpy()
    assert diff[0] == 7200, "CEST should be 2 hours ahead of UTC"
    assert diff[1] == 7200, "CEST should be 2 hours ahead of UTC"
    assert diff[2] == 3600, "CET should be 1 hours ahead of UTC"


def test_uts_parsing(datadir):
    utc = datagram_from("csv_utc.json", datadir)
    cet = datagram_from("csv_cet.json", datadir)
    diff = utc["0"].uts.to_numpy() - cet["0"].uts.to_numpy()
    assert (diff == 0).all(), "'uts' column parsing should ignore timezones"


def test_isotimestamp_parsing(datadir):
    utc = datagram_from("csv_utc.json", datadir)
    cet = datagram_from("csv_cet.json", datadir)
    diff = utc["0"].uts.to_numpy() - cet["0"].uts.to_numpy()
    assert (diff == 0).all(), "Z-suffix should override timezone provided in schema"


def test_isotimestamp_parsing_utc(datadir):
    dg = datagram_from("iso_utc.json", datadir)

    assert dg["0"].uts[0] == 1622557825.0, "Z-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[1] == 1622557825.0 + 7200 + 1
    ), "±HH:MM-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[2] == 1622557825.0 + 2
    ), "no suffix with timezone = UTC parsed to 'uts' correctly"


def test_isotimestamp_parsing_cet(datadir):
    dg = datagram_from("iso_cet.json", datadir)
    assert dg["0"].uts[0] == 1622557825.0, "Z-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[1] == 1622557825.0 + 7200 + 1
    ), "±HH:MM-suffix parsed to 'uts' correctly"
    assert (
        dg["0"].uts[2] == 1622557825.0 - 7200 + 2
    ), "no suffix with timezone = CEST parsed to 'uts' correctly"
