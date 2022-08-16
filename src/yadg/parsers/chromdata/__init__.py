"""
This module handles the reading of post-processed chromatography data, i.e.
files containing peak areas, concentrations, or mole fractions.

:mod:`~yadg.parsers.chromdata` loads the processed chromatographic data from the 
specified file, including the peak heights, areas, retention times, as well as the 
concentrations and mole fractions (normalised, unitless concentrations).

.. note:: 

  To parse trace data as present in raw chromatograms, use the 
  :mod:`~yadg.parsers.chromtrace` parser.

Usage
`````
Available since ``yadg-4.2``. The parser supports the following parameters:

.. _yadg.parsers.chromdata.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.ChromData.Params

.. _yadg.parsers.chromdata.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - Inficon Fusion JSON format (``fusion.json``):  
   see :mod:`~yadg.parsers.chromdata.fusionjson`
 - Inficon Fusion zip archive (``fusion.zip``): 
   see :mod:`~yadg.parsers.chromdata.fusionzip`
 - Inficon Fusion csv export (``fusion.csv``): 
   see :mod:`~yadg.parsers.chromdata.fusioncsv`
 - Empa's Agilent LC csv export (``empalc.csv``): 
   see :mod:`~yadg.parsers.chromdata.empalccsv`
 - Empa's Agilent LC excel export (``empalc.xlsx``): 
   see :mod:`~yadg.parsers.chromdata.empalcxlsx`

.. _yadg.parsers.chromdata.provides:

Provides
````````
This raw data is stored, for each timestep, using the following format:

.. code-block:: yaml

  - uts: !!float
    fn:  !!str
    raw:
      sampleid: !!str             # sample name or valve ID
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
