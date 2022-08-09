"""
This parser handles the reading and processing of any tabular files, as long as 
the first line contains the column headers, and the second line an optional
set of units. The columns of the table must be separated using a separator 
(``,`` or ``;`` or ``\\t`` or similar). 

An attempt to deduce the timestamp from column headers is made automatically,
using :func:`yadg.dgutils.dateutils.infer_timestamp_from`. Alternatively, the 
timestamp column(s) and format can be provided using parameters.

Usage
`````
Select :mod:`~yadg.parsers.basiccsv` by supplying ``basiccsv`` to the ``parser`` 
keyword, starting in :class:`DataSchema-4.0`. The parser supports the following 
parameters:

.. _yadg.parsers.basiccsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.BasicCSV.Params

.. admonition:: DEPRECATED in ``yadg-4.2``

    The ``convert`` and ``calfile`` parameters are deprecated as of ``yadg-4.2``
    and will stop working in ``yadg-5.0``.

Provides
````````
The primary functionality of :mod:`~yadg.parsers.basiccsv` is to load the tabular 
data, and determine the Unix timestamp. The headers of the tabular data are taken 
`verbatim` from the file, and appear as ``raw`` data keys.


"""

from .main import process
