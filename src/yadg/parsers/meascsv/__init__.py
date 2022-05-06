"""
This parser handles the reading and processing of the legacy log files created by 
the LabView interface for the MCPT instrument. With a provided calibration, this 
parser calculates the temperature, inlet composition, and the inlet flow of the 
MCPT instrument.

.. warning::

    As of ``yadg-4.0.0``, this parser is deprecated and is no longer maintained.
    Please consider switching to other parsers.

Usage
`````
The use of :mod:`~yadg.parsers.meascsv` can be requested by supplying ``meascsv``
to the ``parser`` keyword in the `dataschema`. The following additional parameters
are supported by the parser:

.. _yadg.parsers.meascsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.MeasCSV.Params

.. _parsers_meascsv_provides:

Provides
````````
The parser is used to extract all of the tabular data in the input file, storing 
them using the column headers as keys. The functionality exposed by this parser
is using :mod:`~yadg.parsers.basiccsv` behind the scenes.

Metadata
````````
The metadata section is currently empty.


"""

from .main import process
