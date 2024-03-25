from yadg.parsers.electrochem.tomatojson import process as extract

supports = {
    "tomato.json",
    "marda:phi-spe",
}

__all__ = ["supports", "extract"]
