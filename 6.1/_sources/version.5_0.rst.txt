**yadg** version 5.0
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v5.0&color=blue&logo=github
  :target: https://github.com/PeterKraus/yadg/tree/5.0
.. image:: https://img.shields.io/static/v1?label=yadg&message=v5.0&color=blue&logo=pypi
  :target: https://pypi.org/project/yadg/5.0/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2023-10-15&color=red&logo=pypi


Developed at Technische Universität Berlin (Berlin, DE) and at Empa (Dübendorf, CH).

New features since ``yadg-4.2`` are:

  - Support for ``DataSchema-5.0``.
  - The output format of ``yadg`` is now a ``NetCDF`` file (``.nc``), as written by the :class:`xarray.DataTree` class.
  - The supplied `dataschemas` are now automatically updated, yielding the latest verison of `dataschema` prior to parsing.
  - Added ``yadg extract`` usage, with optional ``--meta-only`` switch, for a quick data or meta data extraction from individual files. This implements the |marda_extractors|_ inteface.

Backwards-incompatible changes include:

  - Data post-processing within :mod:`yadg` has been removed, following its deprecation in ``yadg-4.2``. All previously included post-processing functionality should be available in ``dgpost-2.0``. If you find functionality that has been broken since ``yadg-4.2`` and which cannot be implemented in **dgpost**, please file an issue on GitHub with example files.
  - The ``yadg update`` functionality is now only for updating `dataschema`; the ability to update `datagrams` has been removed.
  - The parameter ``transpose`` from :mod:`~yadg.parsers.electrochem` parser is no longer available; all electrochemistry data is returned as plain timesteps.
  - The ``valve`` number in the ``fusion-json`` extractor of :mod:`~yadg.parsers.chromtrace` is now stored as ``data`` instead of ``metadata``.

Bug fixes include:

  - the :mod:`~yadg.parsers.electrochem` parser now properly parses files with ``WAIT`` technique;
  - the :mod:`~yadg.parsers.electrochem` parser understands more versions of the ``MB`` technique versions in the ``biologic.mpr`` filetype;
  - the :mod:`~yadg.parsers.electrochem` parser can handle localized versions of data in the ``biologic.mpt`` filetype;
  - the :mod:`~yadg.parsers.chromtrace` parser now properly unzips data when using the ``agilent.dx`` filetype.


.. _marda_extractors: https://github.com/marda-alliance/metadata_extractors

.. |marda_extractors| replace:: MaRDA Metadata Extractors WG