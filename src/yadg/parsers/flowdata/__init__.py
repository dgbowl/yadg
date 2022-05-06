"""
This parser handles the reading and processing of flow meter data. Files parsed 
through this parser are guaranteed to contain the ``"flow"`` entry in the derived
keys.

Usage
`````
The use of :mod:`~yadg.parsers.flowdata` can be requested by supplying ``flowdata``
as the ``parser`` keyword in the `dataschema`. The following list of parameters is 
supported by the parser:

.. _yadg.parsers.flowdata.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.FlowData.Params

.. _yadg.parsers.flowdata.formats:

Formats
```````
The formats currently supported by the parser are:

 - DryCal log file text output (``txt``): 
   :mod:`~yadg.parsers.flowdata.drycal`
 - DryCal log file tabulated output (``csv``): 
   :mod:`~yadg.parsers.flowdata.drycal`
 - DryCal log file document file (``rtf``): 
   :mod:`~yadg.parsers.flowdata.drycal`

.. _yadg.parsers.flowdata.provides:

Provides
````````
The parser is used to extract all tabular data in the input file. Additionally,
the parser automatically assigns a best-guess value as ``flow`` in the ``derived`` 
entry. This behaviour can be modified by supplying either the ``calfile``
and/or ``convert`` parameters. 

This parser processes additional calibration information analogously to 
:mod:`~yadg.parsers.basiccsv`. 
        
Metadata
````````
The metadata section currently stores all metadata available from the raw flow
data files, including information about the measuring device.

"""
from .main import process
