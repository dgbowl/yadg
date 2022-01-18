.. _object_schema:

What is a `schema`
``````````````````
A `schema` is an object defining the files and folders to be processed by 
**yadg**, as well as the types of parsers and the parser options to be applied.
One can think of a `schema` as a representation of a single experiment, 
containing measurements from multiple sources (or devices) and following a 
succession of experimental `steps`.

.. admonition:: TODO

    https://gitlab.empa.ch/krpe/yadg/-/issues/8

    The syntax of `schema` will change from a json dictionary to a YAML file 
    in version 5.0.

An example is a simple catalytic test with a temperature ramp. The goal of such 
an experiment may be to measure the catalytic conversion as a function of 
temperature, and then calculate the activation energy of the catalytic reaction. 
The monitored devices and their filetypes are:

- the inlet flow and pressure meters -> ``csv`` data in ``foo.csv``
- the temperature controller -> ``csv`` data in ``bar.csv``
- the gas chromatograph -> Fusion ``json`` data in ``./GC/`` folder

Despite these three devices measuring concurrently, we would have to specify 
three separate `steps` in the schema to process all relevant output files:

.. code-block:: json

    {
        "metadata": {"provenance": "manual", "schema_version": "1.0"},
        "steps": [{
            "parser": "basiccsv",
            "import": {"files": ["foo.csv"]},
            "tag": "flow",
            "parameters": {}
        },{
            "parser": "basiccsv",
            "import": {"files": ["bar.csv"]}
        },{
            "parser": "chromtrace",
            "import": {"folders": ["./GC/"]},
            "parameters": {"tracetype": "fusion"}
        }]
    }

A valid `schema` is therefore a :class:`(dict)`, with a top-level ``"metadata"``
entry describing the schema provenance and version; and a top-level ``"steps"``
entry, which is a :class:`(list)` containing the definitions for the experimental
`steps`. Each `step` within the `schema` is a :class:`(dict)`. In each `step`, 
the entries ``"parser"`` and ``"import"`` have to be specified, telling **yadg** 
which `parser` to use and which files or folders to process, respectively.

Other allowed entries are: 

- ``"tag"`` :class:`(str)`, a tag describing a certain `step`; 
- ``"export"`` :class:`(str)`, a path defining the location for individual 
  export of `steps`; and 
- ``"parameters"`` :class:`(dict)`, an object for specifying additional 
  parameters for the `parser`.

However, a `schema` can contain more than one `step` with the same ``"parser"``
entry. This is valuable if one wants to split a certain timeseries into smaller
chunks -- in the above example, if we want to determine the activation energy of 
a catalytic reaction, it may be helpful to ensure a new ``csv`` file is created 
each time the temperature setpoint is changed. The `schema` might the look as 
follows:


.. code-block:: json
   :emphasize-lines: 12-14,16-18,20-22

    {
        "metadata": {"provenance": "manual", "schema_version": "1.0"},
        "steps": [{
            "datagram": "basiccsv",
            "import": {"files": ["foo.csv"]},
            "tag": "flow",
            "parameters": {}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["01-temp.csv"]}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["02-temp.csv"]},
            "tag": "340 deg C"
        },{
            "datagram": "basiccsv",
            "import": {"files": ["03-temp.csv"]},
            "tag": "320 deg C"
        },{
            "datagram": "basiccsv",
            "import": {"files": ["04-temp.csv"]},
            "tag": "300 deg C"
        },{
            "datagram": "basiccsv",
            "import": {"files": ["05-temp.csv"]}
        },{
            "datagram": "gctrace",
            "import": {"folders": ["./GC/"]},
            "parameters": {"tracetype": "fusion"}
        }]
    }

From this `schema`, the catalytic conversion can be obtained by combining the
inlet flow and outlet composition (GC) data. The activation energy can then be 
calculated by looking up the conversion corresponding to the conditions at the 
end of each temperature ramp `step` highlighted above, and performing an
Arrhenius fit.

.. note::

    Further information about the `schema` can be found in the documentation of 
    the `schema` validator function: :func:`yadg.core.validators.validate_schema`.
    The whole `schema` specification is present in the :mod:`yadg.core.spec_schema`
    module.
