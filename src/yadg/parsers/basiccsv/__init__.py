"""
Handles the reading and processing of any tabular files, as long as the first line
contains the column headers. By default, the second should contain the units. The
columns of the table must be separated using a separator such as ``,``, ``;``,
or ``\\t``.

.. warning::

  Since ``yadg-5.0``, the parser handles sparse tables (i.e. tables with missing
  data) by back-filling empty cells with ``np.NaNs``.

.. note::

  :mod:`~yadg.parsers.basiccsv` attempts to deduce the timestamp from the column
  headers, using :func:`yadg.dgutils.dateutils.infer_timestamp_from`. Alternatively,
  the column(s) containing the timestamp data and their format can be provided using
  parameters.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.basiccsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.BasicCSV

Schema
``````
The primary functionality of :mod:`~yadg.parsers.basiccsv` is to load the tabular
data, and determine the Unix timestamp. The headers of the tabular data are taken
`verbatim` from the file, and appear as ``data_vars`` of the :class:`xarray.Dataset`.
The single ``coord`` for the ``data_vars`` is the deduced Unix timestamp, ``uts``.

.. code-block:: yaml

  xr.Dataset:
    coords:
      uts:            !!float               # Unix timestamp
    data_vars:
      {{ headers }}:  (uts)                 # Populated from file headers

Module Functions
````````````````

"""

from .main import process

__all__ = ["process"]
