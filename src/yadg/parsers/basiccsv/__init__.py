"""
This parser handles the reading and processing of any tabular files, as long as 
the first line contains the column headers, and the second line an optional
set of units. The columns of the table must be separated using a separator 
(``,`` or ``;`` or ``\\t`` or similar). 

A rudimentary column-converting functionality is also included. This allows the user 
to specify linear combinations of columns, and can be used to apply a calibration 
to the columnar data.

An attempt to deduce the timestamp from column headers is made automatically,
using :func:`yadg.dgutils.dateutils.infer_timestamp_from`. Alternatively, the 
timestamp column(s) and format can be provided using parameters.

Usage
`````
The use of :mod:`~yadg.parsers.basiccsv` can be requested by supplying
``basiccsv`` as an argument to the ``parser`` keyword of the `dataschema`.
The parser supports the following parameters:

.. _yadg.parsers.basiccsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.BasicCSV.Params

.. note::

    The specification of the calibration dictionary that ought to be passed via 
    ``convert`` (or stored as json in ``calfile``) is described in 
    :func:`~yadg.parsers.basiccsv.main.process_row`.

.. note::
    
    The ``calfile`` and ``convert`` functionalities allow for combining and 
    converting the raw data present in the data files into new entries, which
    are stored in the ``derived`` entry of each timestep.


Provides
````````
The primary functionality of :mod:`~yadg.parsers.basiccsv` is to load the tabular 
data, and determine the Unix timestamp. The headers of the tabular data are taken 
`verbatim` from the file, and appear as ``raw`` data keys.

Metadata
````````
The metadata section is currently empty.

"""

from .main import process
