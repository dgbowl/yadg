"""
This parser handles the reading and processing of the legacy log files created by 
the LabView interface for the MCPT instrument. With a provided calibration, this 
parser calculates the temperature, inlet composition, and the inlet flow of the 
MCPT instrument.

.. admonition:: DEPRECATED in ``yadg-4.0``

    As of ``yadg-4.0``, this parser is deprecated and should not be used for new data.
    Please consider switching to the :mod:`~yadg.parsers.basiccsv` parser.

Usage
`````
Available since ``yadg-3.0``. Deprecated since ``yadg-4.0``. The parser supports the 
following parameters:

.. _yadg.parsers.meascsv.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.MeasCSV.Params

.. _parsers_meascsv_provides:

Provides
````````
The parser is used to extract all of the tabular data in the input file, storing 
them in the same format as :mod:`~yadg.parsers.basiccsv`, using the column headers 
as keys. The functionality exposed by this parser is using :mod:`~yadg.parsers.basiccsv` 
behind the scenes.


"""

from .main import process
