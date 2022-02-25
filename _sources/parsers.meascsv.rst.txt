``meascsv``: Legacy MCPT log file parser
========================================
The ``meascsv`` parser handles the reading and processing of the legacy log files
created by the LabView interface for the MCPT instrument. 

With a provided calibration, this parser calculates the temperature, inlet composition,
and the inlet flow of the MCPT instrument.

Usage
-----
The use of ``meascsv`` can be specified using the ``"parser"`` keyword in the
`schema`. The allowed list of ``"parameters"`` is a subset of that available for
:ref:`basiccsv<basiccsv_rst>`:

- ``"calfile"`` :class:`(str)`: A calibration file in a json format.
- ``"convert"`` :class:`(dict)`: Calibration/conversion specification in a dictionary,
  overrides that provided in ``"calfile"``. The processing of the combined calibration
  is handled in :func:`yadg.parsers.basiccsv.process_row`.

.. _parsers_meascsv_provides:

Provides
--------
The parser is used to extract all tabular data in the input file, storing them in the
``"raw"`` entry, using the column headers as keys.
        
The ``"metadata"`` section is currently empty.

If the ``"calfile"`` and/or ``"convert"`` is supplied, this parser processes the 
information analogously to :ref:`basiccsv<basiccsv_rst>`, storing the results in
the ``"derived"`` entry. Additionally, the values of all ``"derived"`` entries that 
do not start with ``flow`` or ``T`` are interpreted as components of the inlet flow
mixture; they are normalised to their respective mol fractions in ``"xin"``.
