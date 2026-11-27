"""Regression test for filetypes accepted by extractors."""

import importlib
import pkgutil
import typing

from dgbowl_schemas.yadg.dataschema import ExtractorFactory

import yadg.extractors
from yadg.extractors import FiletypeName

# Accepted by the dataschema but deprecated
DEPRECATED = {"fusion.zip"}


def test_filetypes_match() -> None:
    """The filetypes accepted by `extract` must match the available modules and the dataschema."""
    # Filetypes in the `extract` type hint
    hinted = set(typing.get_args(FiletypeName))

    # Filetypes in the extractor modules
    prefix = "yadg.extractors."
    modules = {
        info.name.removeprefix(prefix)
        for info in pkgutil.walk_packages(yadg.extractors.__path__, prefix)
        if hasattr(importlib.import_module(info.name), "extract")
    }

    # Filetypes accepted by the dataschema
    extractor = ExtractorFactory.model_json_schema()["properties"]["extractor"]
    schema = set(extractor["discriminator"]["mapping"]) - DEPRECATED

    assert hinted == modules
    assert hinted == schema
