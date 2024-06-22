"""
This is an example extractor, used mainly for testing of the :mod:`yadg` package.
It provides no real functionality.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Example


Schema
``````
The output schema is only defined for the ``tomato.json`` filetype.

.. code-block:: yaml

  datatree.DataTree:
    coords:
      uts:              !!float      # The current timestamp
    data_vars:
      {{ param_keys }}  (None)       # All parameter key/value pairs

Metadata
````````
No metadata is returned.

.. codeauthor::
    Peter Kraus

"""

from pydantic import BaseModel
from yadg import dgutils
from datatree import DataTree


def extract(
    *,
    fn: str,
    parameters: BaseModel,
    **kwargs: dict,
) -> DataTree:
    kwargs = {} if parameters is None else parameters.model_dump()
    if "parser" in kwargs:
        del kwargs["parser"]
    data_vals = {k: [v] for k, v in kwargs.items()}
    data_vals["uts"] = [dgutils.now()]
    meta_vals = {}
    return DataTree(dgutils.dicts_to_dataset(data_vals, meta_vals, fulldate=False))
