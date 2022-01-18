.. _object_datagram:

What is a `datagram`
````````````````````
The `datagram` is a structured and annotated representation of both raw and 
processed data. Here, "raw data" corresponds to data present in the output files
as they come out of an instrument directly, while "processed data" corresponds 
to data after any processing -- whether the processing is applying a calibration 
curve, or a more involved transformation, such as deriving :math:`Q_0` and 
:math:`f_0` from :math:`\Gamma(f)` in the :mod:`yadg.parsers.qftrace` module. 

The `datagram` is designed to be a mirror of the raw data files, with:

    - uncertainties of measured datapoints
    - units associated with data
    - a consistent data structure for timestamped traces
    - a consistent variable mapping between different filetypes

Additionally, the `datagram` is  annotated by relevant metadata, including:

    - version information
    - clear provenance of raw data 
    - documentation of any post-processing
    - uniform data timestamping between all `datagrams`

.. note::
    The datagram does not guarantee that timesteps are normalized. This means entries 
    may or may not be present in all timesteps within a step. An example of this would
    be if an analyte appears in chromatographic traces after the first timesteps - the 
    entry corresponding to the concentration of that analyte is **not** back-filled by
    **yadg**.

The basic structure of a `datagram` is as follows:

.. code-block:: json

    {
        "metadata": {
            "yadg": {"version": "4.0.0", "command": "pytest"},
            "date": "2021-09-29 09:20:00",
            "input_schema": {"..."},
            "datagram_version": "4.0.0"
        },
        "steps": [
            {
                "metadata": {
                    "tag": "flow",
                    "parser": {"meascsv": {"version": "4.0.0"}}
                },
                "data": [
                    {
                        "uts": 1632900000.0,
                        "fn": "foo.csv", 
                        "raw": {
                            "flow": {"n": 15.0, "s": 0.1, "u": "ml/min"},                    
                            "C3H8": {"n": 0.0305, "s": 0.0010, "u": " "}, 
                            "O2": {"n": 0.0895, "s": 0.0010, "u": " "}, 
                            "N2": {"n": 0.8800, "s": 0.0100, "u": " "}
                        }
                    },{
                        "uts": 1632900060.0,
                        "fn": "foo.csv", 
                        "raw": {
                            "flow": {"n": 14.9, "s": 0.1, "u": "ml/min"},                    
                            "C3H8": {"n": 0.0304, "s": 0.0010, "u": " "}, 
                            "O2": {"n": 0.0896, "s": 0.0010, "u": " "}, 
                            "N2": {"n": 0.8800, "s": 0.0100, "u": " "}
                        }
                    },{
                        "uts": 1632900120.0,
                        "fn": "foo.csv",
                        "raw": {
                            "flow": {"n": 15.0, "s": 0.1, "u": "ml/min"},                    
                            "C3H8": {"n": 0.0305, "s": 0.0010, "u": " "}, 
                            "O2": {"n": 0.0900, "s": 0.0010, "u": " "}, 
                            "N2": {"n": 0.8795, "s": 0.0100, "u": " "}
                    },{
                        "uts": 1632900180.0,
                        "fn": "foo.csv",
                        "raw": {
                        "flow": {"n": 15.0, "s": 0.1, "u": "ml/min"},                    
                            "C3H8": {"n": 0.0302, "s": 0.0010, "u": " "}, 
                            "O2": {"n": 0.0897, "s": 0.0010, "u": " "}, 
                            "N2": {"n": 0.8801, "s": 0.0100, "u": " "}
                        }
                    }
                ]
            }
        ]
    }

The `datagram` is a :class:`(dict)` which always contains two top-level entries:

#. The ``"metadata"`` :class:`(dict)` with information about:

    - the version of **yadg** and the execution command used to generate the `datagram`;
    - a copy of the `schema` used to created the `datagram`;
    - the version of the `datagram`; and
    - the `datagram` creation timestamp formatted according to ISO8601.

#. The ``"steps"`` :class:`(list[dict])` containing the data. The length of this
   array matches the length of the `schema` used to generate the `datagram`. Each 
   element within the ``"steps"`` :class:`(list[dict])` has further mandatory entries: 

    - The `step` specific ``"metadata"`` :class:`(dict)`, which contains:
        
        - the ``"tag"`` :class:`(str)` entry from the `schema`, 
        - information about the ``"parser"`` :class:`(dict)` used for this `step`
        
    - The ``"data"`` :class:`(list[dict])` entry contains the actual data, organised as 
      a time series. Each entry in ``"data"`` has:
       
       - a Unix timestamp in its ``"uts"`` :class:`(float)` entry,
       - a filename of the raw data in its ``"fn"`` :class:`(str)` entry,
       - a ``"raw"`` :class:`(dict)` entry containing any data directly from ``"fn"``.
       - a ``"derived"`` :class:`(dict)` entry containing any post-processed data.
       
  All measurement (floating-point) data has to be provided using the 
  ``"property": {"n": value, "s": error, "u": "unit"}`` syntax, where both 
  ``"n"`` and ``"s"`` are :class:`(float)` and ``"u"`` is :class:`(str)`. The 
  data can be organised in nested data structures, however it is recursively validated.

  In most cases, the data in ``"raw"`` or ``"derived"`` will consist of a single value
  per `timestep`. However, it is also possible to store lists of data in each 
  `timestep`. Generally, **yadg** will store such data under a ``"traces"`` key in the
  appropriate ``"raw"`` or ``"derived"`` entry: 
  
  .. code-block:: json

    "raw": {
        "traces": {
            "FID": {
                "t": {"n": [0, 1, 2, 3, 4], "s": [0.1, 0.1, 0.1, 0.1, 0.1], "u": "s"},
                "y": {"n": [5, 6, 9, 9, 4], "s": [0.5, 0.5, 0.5, 0.5, 0.5], "u": " "},
            }
        }
    }
     
  The above example shows how a chromatographic trace might be stored. At each 
  `timestep`, multiple values of ``"t"`` as well as ``"y"`` are recorded and stored in
  a :class:`(list)`, along with their uncertainties; the unit applies to each element
  in the array.

.. note::
    Futher information about the `datagram` can be found in the documentation of
    the `datagram` validator function: :func:`yadg.core.validators.validate_datagram`,
    as well as in the documentation of each parser.