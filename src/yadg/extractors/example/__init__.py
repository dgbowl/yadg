"""
This is an example extractor, used mainly for testing of the :mod:`yadg` package.
It provides no real functionality.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.Dummy

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - tomato's JSON file (``tomato.json``)

Schema
``````
The output schema is only defined for the ``tomato.json`` filetype.

.. code-block:: yaml

  xr.Dataset:
    coords:
      uts:           !!float
    data_vars:
      {{ entries }}  (uts)        # Elements present in the "data" entry

The value of every element of ``data`` is assigned a deviation of 0.0.

Module Functions
````````````````

"""

from pydantic import BaseModel
import json
from ... import dgutils
from yadg.parsers.basiccsv.main import append_dicts, dicts_to_dataset
from datatree import DataTree


def extract(
    *,
    fn: str,
    parameters: BaseModel,
    **kwargs: dict,
) -> DataTree:
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

    filetype
        Accepts ``tomato.json`` as an optional "dummy instrument" filetype from
        :mod:`tomato`.

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_5_0.step.Dummy`.

    Returns
    -------
    :class:`xarray.Dataset`

    """

    kwargs = {} if parameters is None else parameters.dict()
    if "parser" in kwargs:
        del kwargs["parser"]
    data_vals = {k: [v] for k, v in kwargs.items()}
    data_vals["uts"] = [dgutils.now()]
    meta_vals = {}
    return dicts_to_dataset(data_vals, meta_vals, fulldate=False)


__all__ = ["supports", "extract"]
