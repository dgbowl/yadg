from yadg.parsers.xpstrace.phispe import process as extract

supports = {
    "phi.spe",
    "marda:phi-spe",
}

__all__ = ["supports", "extract"]
