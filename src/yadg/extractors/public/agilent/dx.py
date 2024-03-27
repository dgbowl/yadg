from yadg.parsers.chromtrace.agilentdx import process as extract

supports = {
    "agilent.dx",
    "marda:agilent-dx",
}

__all__ = ["supports", "extract"]
