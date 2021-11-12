:orphan:

.. _object_datagram:

What is a `datagram`
````````````````````
The `datagram` is a structured and annotated representation of both raw and 
processed data. Here, "raw data" corresponds to data present in the output files
as they come out of an instrument directly, while "processed data" corresponds 
to data after any processing -- whether the processing is applying a calibration 
curve, or a more involved transformation, such as deriving :math:`Q_0` and 
:math:`f_0` from :math:`\Gamma(f)` in the :mod:`yadg.parsers.qftrace` module. 
The `datagram` is designed to be:

- annotated by relevant metadata, including:
    - version information
    - clear provenance of data 
    - documentation of any post-processing
    - uniform data timestamping between all `datagrams`

The basic structure of a `datagram` is as follows:

.. code-block:: json

    {
        "metadata": {
            "yadg": {"version": "4.0.0", "command": "pytest"},
            "date": "2021-09-29 09:20:00"
        },
        "steps": [
            {
                "metadata": {
                    "fn": "foo.csv",
                    "tag": "flowdata",
                    "input": {
                        "parser": "basiccsv",
                        "import": {"files": ["foo.csv"]},
                        "tag": "flowdata",
                        "parameters": {}
                    }
                },
                "data": [
                    {
                        "uts": 1632900000.0, 
                        "flow": [15.0, 0.1, "ml/min"],
                        "xin": {"C3H8": [0.0305, 0.0010, "-"], "O2": [0.0895, 0.0010, "-"], "N2": [0.8800, 0.0100, "-"]}
                    },{
                        "uts": 1632900060.0, 
                        "flow": [14.9, 0.1, "ml/min"],
                        "xin": {"C3H8": [0.0304, 0.0010, "-"], "O2": [0.0896, 0.0010, "-"], "N2": [0.8800, 0.0100, "-"]}
                    },{
                        "uts": 1632900120.0, 
                        "flow": [15.0, 0.1, "ml/min"],
                        "xin": {"C3H8": [0.0305, 0.0010, "-"], "O2": [0.0900, 0.0010, "-"], "N2": [0.8795, 0.0100, "-"]}
                    },{
                        "uts": 1632900180.0, 
                        "flow": [15.0, 0.1, "ml/min"],
                        "xin": {"C3H8": [0.0302, 0.0010, "-"], "O2": [0.0897, 0.0010, "-"], "N2": [0.8801, 0.0100, "-"]}
                    }
                ]
            }
        ]
    }

The `datagram` is a :class:`dict` which always contains two top-level entries:

- The ``"metadata"`` :class:`(dict)` with information about the version of 
  **yadg** as well as the execution command used to generate the `datagram`; and
  the ``"date"`` :class:`(str)` entry, formatted according to ISO8601.
- The ``"steps"`` :class:`(list[dict])`, the length of which matches the length 
  of the `schema` used to generate the `datagram`, i.e. the number of `steps`.

Each element within the ``"steps"`` :class:`(list[dict])` has further mandatory
entries: 

- The `step`\ -specific ``"metadata"`` :class:`(dict)` contains the ``"tag"`` 
  :class:`(str)` entry from the `schema`, as well as a copy of the 
  `step`\ -specific portion of the `schema` itself in the ``"input"`` 
  :class:`(dict)` entry. 
- The ``"data"`` :class:`(list[dict])` entry contains the actual data, 
  organised as a time series. Each entry in ``"data"`` has to have a Unix 
  timestamp in its ``"uts"`` :class:`(float)` entry. All other data has to be
  provided using the ``"property": [value, error, unit]`` syntax, where both 
  ``value`` and ``error`` are :class:`(float)` and ``unit`` is :class:`(str)`.
  The data can be organised in nested data structures, however it is recursively
  validated.

The original "raw data" file has to be specified using a ``"fn"`` :class:`(str)`
entry either once for each `step` in its ``"metadata"`` and for each individual 
timestep in the ``"data"`` :class:`(list[dict])`.

.. note::

    Futher information about the `datagram` can be found in the documentation of
    the`datagram` validator function: :func:`yadg.core.validators.validate_datagram`.