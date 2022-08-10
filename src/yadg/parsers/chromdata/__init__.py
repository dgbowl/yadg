"""
The :mod:`chromdata` parser handles the reading of processed chromatography data, i.e.
files containing peak areas, concentrations, or mole fractions.

.. note:: 

  To parse trace data as present in raw chromatograms, use the 
  :mod:`~yadg.parsers.chromtrace` parser.

Usage
`````
Select :mod:`~yadg.parsers.chromdata` by supplying ``chromdata`` to the ``parser``
keyword, starting in :class:`DataSchema-4.2`. The parser supports the following 
parameters:

.. _yadg.parsers.chromdata.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.ChromData.Params

.. _yadg.parsers.chromdata.formats:

Formats
```````
The formats currently supported by the parser are:

 - Inficon Fusion JSON format (``json``): :mod:`~yadg.parsers.chromdata.fusionjson`
 - Inficon Fusion zip archive (``zip``): :mod:`~yadg.parsers.chromdata.fusionzip`
 - Inficon Fusion csv export (``csv``): :mod:`~yadg.parsers.chromdata.fusioncsv`

.. _yadg.parsers.chromdata.provides:

Provides
````````
:mod:`~yadg.parsers.chromdata`` loads the processed chromatographic data from the 
specified file, including the peak height, and area, as well as the concentration
and mole fraction (normalised, unitless concentration). This raw data is stored, 
for each timestep, using the following format:

.. code-block:: yaml

  raw:
    height:                     # heights of the peak maxima
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    area:                       # integrated areas of the peaks
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    concentration:
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    xout:                       # mole fractions (normalised concentrations)
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: " "}
    retention time:
      "{{ species_name }}":
          {n: !!float, s: !!float, u: " "}

.. note::

    The mole fractions in ``xout`` always sum up to unity. If there is more than
    one outlet stream, or if some analytes remain unidentified, the values in 
    ``xout`` will not be accurate.

"""
from .main import process
