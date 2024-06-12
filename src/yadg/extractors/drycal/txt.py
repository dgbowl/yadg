"""
Handles the reading and processing of volumetric flow meter data exported from the
MesaLabs DryCal software as a txt file.

.. note::

    The date information is missing in the timestamps of the exported files and has to
    be supplied externally.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Drycal_txt

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:            !!float               # Unix timestamp, without date
      data_vars:
        DryCal:         (uts)                 # Standardised flow rate
        DryCal Avg.:    (uts)                 # Running average of the flow rate
        Temp.:          (uts)                 # Measured flow temperature
        Pressure:       (uts)                 # Measured flow pressure

Metadata
````````
The following metadata is extracted:

    - ``product``: Model name of the MesaLabs device.
    - ``serial number``: Serial number of the MesaLabs device.

Uncertainties
`````````````
All uncertainties are derived from the string representation of the floats.

.. codeauthor::
    Peter Kraus

"""

from datatree import DataTree
from yadg.extractors.drycal import common


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    vals = common.sep(fn, "\t", encoding, timezone)
    return DataTree(common.check_timestamps(vals))
