from yadg.parsers.qftrace.labviewcsv import process as extract

supports = {
    "labview.csv",
}

__all__ = ["supports", "extract"]
