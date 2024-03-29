"""
Handles the reading and processing of volumetric flow meter data exported from the
MesaLabs DryCal software as a csv file.

.. note::

    The date information is missing in the timestamps of the exported files and has to
    be supplied externally.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Drycal_csv

Schema
``````
.. code-block:: yaml

    xarray.Dataset:
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

.. codeauthor::
    Peter Kraus

"""

from xarray import Dataset
from yadg.extractors.public.drycal import common


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> Dataset:
    vals = common.sep(fn, ",", encoding, timezone)
    return common.check_timestamps(vals)
