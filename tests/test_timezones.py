import os
import json

import yadg.core
from utils import datadir


def datagram_from(fn, datadir):
    os.chdir(datadir)
    with open(fn, "r") as infile:
        schema = json.load(infile)
    assert yadg.core.validators.validate_schema(schema), "incorrect schema format"
    return yadg.core.process_schema(schema)


def test_timestamp_parsing(datadir):
    utc = datagram_from("ssv_utc.json", datadir)
    assert yadg.core.validators.validate_datagram(utc), "incorrect datagram format"
    cet = datagram_from("ssv_cet.json", datadir)
    assert yadg.core.validators.validate_datagram(cet), "incorrect datagram format"
    assert (
        utc["steps"][0]["data"][0]["uts"] - cet["steps"][0]["data"][0]["uts"] == 7200
    ), "CEST should be 2 hours ahead of UTC"
    assert (
        utc["steps"][0]["data"][1]["uts"] - cet["steps"][0]["data"][1]["uts"] == 3600
    ), "CET should be 1 hour ahead of UTC"


def test_uts_parsing(datadir):
    utc = datagram_from("csv_utc.json", datadir)
    assert yadg.core.validators.validate_datagram(utc), "incorrect datagram format"
    cet = datagram_from("csv_cet.json", datadir)
    assert yadg.core.validators.validate_datagram(cet), "incorrect datagram format"
    assert (
        utc["steps"][0]["data"][0]["uts"] - cet["steps"][0]["data"][0]["uts"] == 0
    ), "'uts' column parsing should ignore timezones"
    assert (
        utc["steps"][0]["data"][1]["uts"] - cet["steps"][0]["data"][1]["uts"] == 0
    ), "'uts' column parsing should ignore timezones"


def test_isotimestamp_parsing(datadir):
    utc = datagram_from("csv_utc.json", datadir)
    assert yadg.core.validators.validate_datagram(utc), "incorrect datagram format"
    cet = datagram_from("csv_cet.json", datadir)
    assert yadg.core.validators.validate_datagram(cet), "incorrect datagram format"
    assert (
        utc["steps"][0]["data"][0]["uts"] - cet["steps"][0]["data"][0]["uts"] == 0
    ), "Z-suffix should override timezone provided in schema"
    assert (
        utc["steps"][0]["data"][1]["uts"] - cet["steps"][0]["data"][1]["uts"] == 0
    ), "Z-suffix should override timezone provided in schema"


def test_isotimestamp_parsing_utc(datadir):
    dg = datagram_from("iso_utc.json", datadir)
    assert yadg.core.validators.validate_datagram(dg), "incorrect datagram format"
    assert (
        dg["steps"][0]["data"][0]["uts"] == 1622557825.0
    ), "Z-suffix parsed to 'uts' correctly"
    assert (
        dg["steps"][0]["data"][1]["uts"] == 1622557825.0 + 7200 + 1
    ), "±HH:MM-suffix parsed to 'uts' correctly"
    assert (
        dg["steps"][0]["data"][2]["uts"] == 1622557825.0 + 2
    ), "no suffix with timezone = UTC parsed to 'uts' correctly"


def test_isotimestamp_parsing_cet(datadir):
    dg = datagram_from("iso_cet.json", datadir)
    assert yadg.core.validators.validate_datagram(dg), "incorrect datagram format"
    assert (
        dg["steps"][0]["data"][0]["uts"] == 1622557825.0
    ), "Z-suffix parsed to 'uts' correctly"
    assert (
        dg["steps"][0]["data"][1]["uts"] == 1622557825.0 + 7200 + 1
    ), "±HH:MM-suffix parsed to 'uts' correctly"
    assert (
        dg["steps"][0]["data"][2]["uts"] == 1622557825.0 - 7200 + 2
    ), "no suffix with timezone = CEST parsed to 'uts' correctly"
