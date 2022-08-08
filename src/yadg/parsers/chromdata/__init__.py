"""
The :mod:`chromdata` parser handles the reading of processed chromatography data, i.e.
files with peak areas, concentrations, or mole fractions.

.. note:: 

  To parse raw chromatograms, use the :mod:`chromtrace` parser.

Usage
`````
The use of :mod:`~yadg.parsers.chromdata` can be requested by supplying ``chromdata``
as an argument to the ``parser`` keyword of the `dataschema`. The parser supports the
following parameters:

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
    height:                     # height of the peak maxima
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    area:                       # integrated area of the peak
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    concentration:              # concentration
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    xout:                       # mole fraction (normalised concentration)
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: " "}

.. note::

    The mole fractions in ``xout`` always sum up to unity. If there is more than
    one outlet stream, or if some analytes remain unidentified, the values in 
    ``xout`` will not be accurate.

Metadata
````````
The metadata collected from the raw file varies greatly by the raw file format. 
See the documentation of each file parser for details. In general, the following
metadata entries are stored for each `step`:

.. code-block:: yaml
  
  params:
    method:   !!str # path or other specifier of the chromatographic method
    sampleid: !!str # sample ID
    username: !!str # username of raw file creator
    version:  !!str # raw file version or program version
    datafile: !!str # original data file location


"""
from .main import process
