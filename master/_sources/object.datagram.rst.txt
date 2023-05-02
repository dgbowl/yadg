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

As of ``yadg-5.0``, the `datagram` is exported as a ``NetCDF`` file. In memory, it is
represented by a :class:`datatree.DataTree`, with individual `steps` as nodes of that
:class:`datatree.Datatree` containing a :class:`xr.Dataset`.

The top level :class:`datatree.DataTree` contains the following metadata stored in its
attributes:

    - the version of yadg and the execution command used to generate the `datagram`;
    - a copy of the `dataschema` used to created the `datagram`;
    - the version of the `datagram`; and
    - the `datagram` creation timestamp formatted according to ISO8601.

The contents of the attribute fields for each `step` will vary depending on the parser
used to create the corresponding :class:`xr.Dataset`. The following conventions are used:

    - a `coord` field ``uts`` contains a Unix timestamp (:class:`float`),
    - uncertainties for entries are stored using separate entries with names composed as
      ``f"{entry}_std_err``

       - the parent ``f"{entry}"`` is pointing to its uncertainty by annotation using
         the ``ancillary_variables`` field,
       - the uncertainty links back to the ``f"{entry}"`` by annotation using the
         ``standard_name`` field.

    - the use of spaces (and other whitespace characters) in the names of entries is to
      be avoided,
    - the use of forward slashes (``/``) in the names of entries is not allowed.