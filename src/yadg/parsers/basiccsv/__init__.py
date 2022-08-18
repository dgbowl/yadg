"""
This parser handles the reading and processing of any tabular files, as long as 
the first line contains the column headers. By default, the second should contain
the units. The columns of the table must be separated using a separator such as 
``,``, ``;``, or ``\\t``. 

.. warning::

  Since ``yadg-4.2``, the parser handles sparse tables (i.e. tables with missing 
  data) by creating sparse `datagrams`, which means that the each element of the 
  header might not be present in each timestep.

.. note::

  :mod:`~yadg.parsers.basiccsv` attempts to deduce the timestamp from the column 
  headers, using :func:`yadg.dgutils.dateutils.infer_timestamp_from`. Alternatively, 
  the column(s) containing the timestamp data and their format can be provided using 
  parameters.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.basiccsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.BasicCSV.Params

.. admonition:: DEPRECATED in ``yadg-4.2``

    The ``sigma``,  ``convert`` and ``calfile`` parameters are deprecated as of 
    ``yadg-4.2`` and will stop working in ``yadg-5.0``.

Provides
````````
The primary functionality of :mod:`~yadg.parsers.basiccsv` is to load the tabular 
data, and determine the Unix timestamp. The headers of the tabular data are taken 
`verbatim` from the file, and appear as ``raw`` data keys:

.. code-block:: yaml

  - uts: !!float
    fn:  !!str
    raw:
        "{{ column_name }}": 
            {n: !!float, s: !!float, u: !!str}


"""

from .main import process
