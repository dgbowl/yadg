.. _basiccsv_rst:

``basiccsv``: Common tabular file parser
========================================
The ``basiccsv`` parser handles the reading and processing of any tabular files,
as long as the first line contains the column headers, and the second line an optional
set of units. The columns must be separated using a separator (``","``, ``";"``, 
``"\t"`` or similar). 

A rudimentary column-converting functionality is also included. This allows the user 
to specify linear combinations of columns, and can be used to apply a calibration 
to the columnar data.

An attempt to deduce the timestamp from column headers is made automatically,
using :func:`yadg.dgutils.dateutils.infer_timestamp_from`; alternatively, the timestamp
column(s) and format can be provided using parameters.

Usage
-----
The use of ``basiccsv`` can be specified using the ``"parser"`` keyword in the
`schema`. Further information can be specified in the ``"parameters"`` :class:`(dict)`:

- ``"sep"`` :class:`(str)`: The separator character for determining columns.
- ``"units"`` :class:`(dict)`: A dictionary containing column names as keys and the 
  corresponding units as values. If this parameter is not specified, units are read
  from the second line in the tabular file.
- ``"calfile"`` :class:`(str)`: A calibration file in a json format.
- ``"convert"`` :class:`(dict)`: Calibration/conversion specification in a dictionary,
  overrides that provided in ``"calfile"``. The processing of the combined calibration
  is handled in :func:`yadg.parsers.basiccsv.process_row`.
- ``"timestamp"`` :class:`(dict)`: Timestamp specification. Processed in
  :func:`yadg.dgutils.dateutils.infer_timestamp_from`.


.. _parsers_basiccsv_provides:

Provides
--------
The primary functionality of ``basiccsv`` is to load the tabular data, and determine
the Unix timestamp. The headers of the tabular data are taken `verbatim` from the file,
and appear as keys in ``"raw"``.
        
The ``"metadata"`` section is currently empty.

The ``"calfile"`` and ``"convert"`` functionalities allow for combining and converting
the ``"raw"`` data into new entries in the ``"derived"`` entry. 

.. note::
    The specification of the calibration dictionary that ought to be passed via 
    ``"convert"`` (or stored as json in ``"calfile"``) is described in 
    :func:`yadg.parsers.basiccsv.process_row`.
