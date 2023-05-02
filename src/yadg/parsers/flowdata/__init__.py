"""
Handles the reading and processing of flow controller or flow meter data.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.flowdata.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.FlowData

.. _yadg.parsers.flowdata.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

  - DryCal log file text output (``drycal.txt``),
    see :mod:`~yadg.parsers.flowdata.drycal`
  - DryCal log file tabulated output (``drycal.csv``),
    see :mod:`~yadg.parsers.flowdata.drycal`
  - DryCal log file document file (``drycal.rtf``),
    see :mod:`~yadg.parsers.flowdata.drycal`

.. _yadg.parsers.flowdata.provides:

Schema
``````
The parser is used to extract all tabular data in the input file. This parser processes
additional calibration information analogously to :mod:`~yadg.parsers.basiccsv`.

Module Functions
````````````````

"""
from .main import process

__all__ = ["process"]
