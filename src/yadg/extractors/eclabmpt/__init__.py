supports = {
    "eclab.mpt",
    "marda:biologic-mpt",
}

from yadg.parsers.electrochem.eclabmpt import process as extract

__all__ = ["supports", "extract"]
