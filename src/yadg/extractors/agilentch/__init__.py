from yadg.parsers.chromtrace.agilentch import process as extract

supports = {
    "agilent.ch",
    "marda:agilent-ch",
}

__all__ = ["supports", "extract"]
