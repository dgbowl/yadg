from yadg.parsers.electrochem.eclabmpr import process as extract

supports = {
    "eclab.mpr",
    "marda:biologic-mpr",
}

__all__ = ["supports", "extract"]
