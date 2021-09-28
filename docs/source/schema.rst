What is a `schema`
``````````````````
A `schema` is an object defining the files and folders to be processed by 
**yadg**, as well as the types of parsers and the parser options to be applied.
One can think of a `schema` as a representation of a single experiment, containing
measurements from multiple sources (or devices) and following a succession of
experimental `steps`.

An example is a simple catalytic test with a temperature ramp. The monitored 
devices and their filetypes are:

- the inlet flow and pressure meters -> ``csv`` data in ``foo.csv``
- the temperature controller -> ``csv`` data in ``bar.csv``
- the gas chromatograph -> Fusion ``json`` data in ``./GC/`` folder

Despite these three devices measuring concurrently, we would have to specify three
separate steps in the schema to process all of these files:

.. code-block:: json

    [
        {
            "datagram": "basiccsv",
            "import": {"files": ["foo.csv"]},
            "parameters": {"tag": "flowdata"}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["bar.csv"]},
            "parameters": {"tag": "tempdata"}
        },{
            "datagram": "gctrace",
            "import": {"folders": ["./GC/"]},
            "parameters": {"tracetype": "fusion"}
        }
    ]

A valid `schema` is therefore a :class:`list`, with each `step` within that `schema`
a :class:`dict`. In each `step`, the entries ``"datagram"`` and ``"import"`` have to
be specified, telling **yadg** which `parser` to use and which files or folders
to process, respectively.

Other allowed entries are: ``"tag"``, for a :class:`str` tag of a certain
`step`; ``"export"``, a :class:`str` defining the location for individual 
export of `step`\ s; and ``"parameters"``, a :class:`dict` for specifying 
additional parameters for the `parser`.

However, a `schema` can contain more than one `step` with the same ``"datagram"``
entry. This is valuable if one wants to split a certain timeseries into smaller
chunks -- for example, if we want to determine the activation energy of a 
catalytic reaction, it may be helpful to ensure a new ``csv`` file is created 
each time the temperature setpoint is changed. The `schema` might look as follows:


.. code-block:: json
   :emphasize-lines: 12-13,16-17,20-21

    [
        {
            "datagram": "basiccsv",
            "import": {"files": ["foo.csv"]},
            "parameters": {"tag": "flowdata"}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["01-temp.csv"]},
            "parameters": {"tag": "ramp up"}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["02-temp.csv"]},
            "parameters": {"tag": "340 deg C"}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["03-temp.csv"]},
            "parameters": {"tag": "320 deg C"}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["04-temp.csv"]},
            "parameters": {"tag": "300 deg C"}
        },{
            "datagram": "basiccsv",
            "import": {"files": ["05-temp.csv"]},
            "parameters": {"tag": "cool down"}
        },{
            "datagram": "gctrace",
            "import": {"folders": ["./GC/"]},
            "parameters": {"tracetype": "fusion"}
        }
    ]

Then, the activation energy can be obtained by finding the conversion (by combining
inlet flow and GC data) that corresponds to the conditions at the end of each 
temperature ramp `step` highlighted above.

Further information about the `schema` can be found in the documentation of the
`schema` validator function: :func:`yadg.core.validators.validate_schema`.
