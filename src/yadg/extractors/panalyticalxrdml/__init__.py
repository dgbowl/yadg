from yadg.parsers.xrdtrace.panalyticalxrdml import process as extract

supports = {
    "panalytical.xrdml",
    "marda:panalytical-xrdml",
}

__all__ = ["supports", "extract"]
