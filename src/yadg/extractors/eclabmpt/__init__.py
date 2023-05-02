from yadg.parsers.electrochem.eclabmpt import process as extract

supports = {
    "eclab.mpt",
    "marda:biologic-mpt",
}

__all__ = ["supports", "extract"]
