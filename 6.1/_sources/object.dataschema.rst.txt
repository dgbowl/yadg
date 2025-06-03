
**yadg** `dataschema`
`````````````````````
A `dataschema` is an object defining the files and folders to be processed by **yadg**, as well as the types of parsers and the parser options to be applied. One can think of a `dataschema` as a representation of a single experiment, containing measurements from multiple sources (or devices) and following a succession of experimental `steps`.

The current version of the `dataschema` is implemented as a Pydantic model in the class :obj:`~dgbowl_schemas.yadg.dataschema.DataSchema` of the :mod:`dgbowl_schemas.yadg` module. The following (previous) versions of the `dataschema` are available in the same repository:

- :class:`dgbowl_schemas.yadg.dataschema_6_0.DataSchema`
- :class:`dgbowl_schemas.yadg.dataschema_5_1.DataSchema`
- :class:`dgbowl_schemas.yadg.dataschema_5_0.DataSchema`
- :class:`dgbowl_schemas.yadg.dataschema_4_2.DataSchema`
- :class:`dgbowl_schemas.yadg.dataschema_4_1.DataSchema`
- :class:`dgbowl_schemas.yadg.dataschema_4_0.DataSchema`

An example is a simple catalytic test with a temperature ramp. The goal of such an experiment may be to measure the catalytic conversion as a function of temperature, and then calculate the activation energy of the catalytic reaction. The monitored devices and their filetypes are:

- the inlet flow and pressure meters -> ``csv`` data in ``foo.csv``
- the temperature controller -> ``csv`` data in ``bar.csv``
- the gas chromatograph -> Fusion ``json`` data in ``./GC/`` folder

Despite these three devices measuring concurrently, we would have to specify three separate `steps` in the schema to process all relevant output files:

.. literalinclude:: dataschema.json
  :language: json

As we set ``step_defaults -> locale`` to ``de_DE``, the numbers in the localized files (such as the ``csv`` data) will be expected to use ``,`` as a decimal separator. These ``step_defaults`` can be overriden in each *step* using the ``extractor`` entry, see the ``steps -> [0] -> extractor -> locale`` entry which is set to ``en_GB``.

.. note::

    Further information about the `dataschema` can be found in the documentation of
    the :mod:`dgbowl_schemas.yadg` module.

