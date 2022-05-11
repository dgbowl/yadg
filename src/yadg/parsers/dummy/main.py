from pydantic import BaseModel
import json
from ... import dgutils


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
    """
    A dummy parser.

    This parser simply returns the current time, the filename provided, and any
    ``kwargs`` passed.

    In case the provided ``filetype`` is a ``tomato.json`` file, this is a json
    data file from the :mod:`tomato` package, which should contain a :class:`list`
    of ``{"value": float, "time": float}`` datapoints in its ``data`` entry.

    Parameters
    ----------
    fn
        Filename to process

    encoding
        Not used.

    timezone
        Not used

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg_dataschema.dataschema_4_1.parameters.Dummy`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned by the dummy parser. The full date is always returned.

    """
    if hasattr(parameters, "filetype") and parameters.filetype == "tomato.json":
        with open(fn, "r") as inf:
            jsdata = json.load(inf)
        ret = []
        for p in jsdata["data"]:
            ts = {
                "uts": p["time"],
                "fn": fn,
                "raw": {"value": {"n": p["value"], "s": 0.0, "u": " "}},
            }
            ret.append(ts)
        return ret, None, False
    else:
        kwargs = {} if parameters is None else parameters.dict()
        if "parser" in kwargs:
            del kwargs["parser"]
        result = {"uts": dgutils.now(), "fn": str(fn), "raw": kwargs}

        return [result], None, True
