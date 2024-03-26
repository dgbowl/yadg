from yadg.parsers.xrdtrace.panalyticalcsv import process as extract

supports = {
    "panalytical.csv",
}

__all__ = ["supports", "extract"]
