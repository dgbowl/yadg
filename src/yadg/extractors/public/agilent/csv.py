from yadg.parsers.chromtrace.agilentcsv import process as extract

supports = {
    "agilent.csv",
}

__all__ = ["supports", "extract"]
