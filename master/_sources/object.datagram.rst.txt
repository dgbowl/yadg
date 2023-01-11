**yadg** `datagram`
```````````````````
The `datagram` is a structured and annotated representation of raw data. Here, 
"raw data" strictly denotes the data present in the parsed files, as they come out of an 
instrument directly. It may therefore also contain derived data (e.g. data processed using
a calibration curve in chromatography, or a more involved transformation in electrochemistry), 
while referring to them as "raw data", since they are present in the parsed files.

The `datagram` is designed to be a FAIR representation of the parsed files, with:

    - uncertainties of measured datapoints;
    - units associated with data;
    - a consistent data structure for timestamped traces;
    - a consistent variable mapping between different filetypes.

Additionally, the `datagram` is annotated by relevant metadata, including:

    - version information;
    - clear provenance of the data;
    - uniform data timestamping within and between all `datagrams`.

.. note::

    The datagram does not guarantee that the data in the `timesteps` is normalized. 
    This means entries may or may not be present in all timesteps within a step. An 
    example of this would be if an analyte appears in chromatographic traces after the 
    first timesteps - the entry corresponding to the concentration of that analyte is 
    **not** back-filled by yadg.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/4

    The specification of the `datagram` schema should be moved to a Pydantic-based
    model. This feature is expected to be included in ``yadg-5.0``.

As of `yadg-4.0`, the `datagram` is a :class:`dict` which always contains two top-level 
entries:

#. The ``metadata`` :class:`dict` with information about:

    - the version of yadg and the execution command used to generate the `datagram`;
    - a copy of the `dataschema` used to created the `datagram`;
    - the version of the `datagram`; and
    - the `datagram` creation timestamp formatted according to ISO8601.

#. The ``steps`` :class:`list[dict]` containing the data. The length of this
   array matches the length of the ``steps`` in the `dataschema` used to generate the 
   `datagram`. Each element within the ``steps`` has further mandatory entries: 

    - The `step` specific ``metadata`` formatted as a :class:`dict`
    - The ``data`` :class:`list[dict]`, containing the actual data, organised as 
      a time series. Each entry in ``"data"`` has:
       
       - a Unix timestamp in its ``uts`` :class:`float` entry,
       - a filename of the raw data in its ``fn`` :class:`str` entry,
       - a ``raw`` :class:`dict` entry containing any data directly from ``fn``.
       
All measurement (floating-point) data has to be provided using the ``"property": {"n": 
value, "s": error, "u": "unit"}`` syntax, where both ``"n"`` and ``"s"`` are 
:class:`float` and ``"u"`` is :class:`str`. The data can be organised in nested data 
structures, however it is recursively validated.

In most cases, the data in will consist of a single value per `timestep`. However, it 
is also possible to store lists of data in each `timestep`. Generally, yadg will store 
such data under a ``traces`` key in the appropriate ``raw`` or ``derived`` entry: 
  
  .. code-block:: json

    "raw": {
        "traces": {
            "FID": {
                "t": {"n": [0, 1, 2, 3, 4], "s": [0.1, 0.1, 0.1, 0.1, 0.1], "u": "s"},
                "y": {"n": [5, 6, 9, 9, 4], "s": [0.5, 0.5, 0.5, 0.5, 0.5], "u": " "},
            }
        }
    }
     
The above example shows how a chromatographic trace might be stored. At each `timestep`, 
multiple values of ``"t"`` and ``"y"`` are recorded and stored in a :class:`list`, along 
with their uncertainties; the unit applies to each element in the array.

.. note::
    Futher information about the `datagram` can be found in the documentation of
    the `datagram` validator function: :func:`yadg.core.validators.validate_datagram`,
    as well as in the documentation of each parser.