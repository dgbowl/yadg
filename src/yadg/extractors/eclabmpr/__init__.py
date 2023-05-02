supports = {
    "eclab.mpr",
    "marda:biologic-mpr",
}

from yadg.parsers.electrochem.eclabmpr import process as extract

__all__ = ["supports", "extract"]
