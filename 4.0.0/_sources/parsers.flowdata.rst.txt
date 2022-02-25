``flowdata``: Flow data parser
==============================
The ``flowdata`` parser handles the reading and processing of flow meter data. Files
parsed through this parser are guaranteed to contain the ``"flow"`` entry in the derived
keys.

Usage
-----
The use of ``flowdata`` can be specified using the ``"parser"`` keyword in the
`schema`. The allowed list of ``"parameters"`` is a subset of that available for
:ref:`basiccsv<basiccsv_rst>`:

- ``"filetype"`` :class:`(str)`: The file type of the raw data file. 
  See :ref:`here<parsers_flowdata_formats>` for details.
- ``"calfile"`` :class:`(str)`: A calibration file in a json format.
- ``"convert"`` :class:`(dict)`: Calibration/conversion specification in a dictionary,
  overrides that provided in ``"calfile"``. The processing of the combined calibration
  is handled in :func:`yadg.parsers.basiccsv.process_row`.
- ``"date"`` :class:`(str)`: Optional date specification for the ``DryCal`` parser.

.. _parsers_flowdata_provides:

Provides
--------
The parser is used to extract all tabular data in the input file, storing them in the
``"raw"`` entry, using the column headers as keys.
        
The ``"metadata"`` section currently stores all metadata available from the flowdata files.

The ``flowdata`` parser automatically assigns a best-guess value to ``"flow"`` in the 
``"derived"`` keys. This behaviour can be modified by supplying either the ``"calfile"``
and/or ``"convert"``. 

This parser processes calibration information analogously to 
:ref:`basiccsv<basiccsv_rst>`, storing the results in the ``"derived"`` entry. 