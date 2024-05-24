**yadg** version 5.1
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v5.1&color=blue&logo=github
  :target: https://github.com/PeterKraus/yadg/tree/5.1
.. image:: https://img.shields.io/static/v1?label=yadg&message=v5.1&color=blue&logo=pypi
  :target: https://pypi.org/project/yadg/5.1/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2024-XX-YY&color=red&logo=pypi


Developed in the |concat_lab|_ at Technische Universität Berlin (Berlin, DE).

New features since ``yadg-5.0`` are:

  - Support for Touchstone ``.sNp`` files using the :mod:`yadg.extractors.touchstone.snp` extractor. Test files are truncated to first 100 lines, they were obtained from the following DOIs:

    - ``Device_r_*um.s1p`` from https://zenodo.org/doi/10.5281/zenodo.7850136
    - ``SCENARIO*_pulserside_30k_3G.s1p`` from https://zenodo.org/doi/10.5281/zenodo.10016477
    - ``CABLE_3_5MM_1N_TYPE_CONNECTORS.S2P`` from https://zenodo.org/doi/10.5281/zenodo.10016477
    - ``Fig8_*cm.s1p`` from https://zenodo.org/doi/10.5281/zenodo.10222705
    - ``VNA_radial_middle.s*p`` from https://zenodo.org/doi/10.5281/zenodo.7339709

  - Support for EZChrom ``.dat`` files using the :mod:`yadg.extractors.ezchrom.dat` extractor. Test files were provided by Z. Asahi from FU Berlin, and J. Schumann from HU Berlin. The data extracted from the ``.dat`` files is cross-checked against the data obtained from ``.asc`` files using the :mod:`yadg.extractors.ezchrom.asc` extractor.

Other changes in ``yadg-5.1`` are:

  - The dataschema has been simplified, eliminating parsers in favour of extractors.
  - The code has been reorganised to highlight the extractor functionality in favour of parsers.
  - Locale-aware functionality now uses :mod:`babel` instead of the built-in :mod:`locale` module. This means the ``locale`` argument should now be a :class:`str` containing at least the 2-letter country code, ideally also a territory (e.g. ``en_US`` or ``de_CH``). As of ``yadg-5.1``, no :func:`locale.setlocale` is called, making locale procesing in **yadg** thread-safe.

Bug fixes in ``yadg-5.1`` include:

  - Fixed incorrect unit assignment when ``/`` was substituted to ``_`` in column names.
  - Fixed incorrect annotation of ancillary variables: ``standard error`` should be ``standard_error``.
  - Fixed incorrect parsing of units in the :mod:`yadg.extractors.ezchrom.asc` parser. Now, the ``25 μV`` unit will be correctly replaced by just ``μV`` (without modifying data), which can be understood by :mod:`pint`.
  - Added several new I-range values to :mod:`yadg.extractors.eclab` parsers. Now, I-range values up to 130 are supported.
  - Fixed incorrect column name (``Energy`` to ``|Energy|``) in :mod:`yadg.extractors.eclab.mpr`.
  - Removed column renaming for ``Analog IN 1`` and ``Analog IN 2`` to maintain consistency within :mod:`yadg.extractors.eclab`.
  - Reworked parsing of ``.mpt`` file headers in :mod:`yadg.extractors.eclab.mpt`. The parser is now more stable, and the original labels are used without renaming.

.. _concat_lab: https://tu.berlin/en/concat

.. |concat_lab| replace:: ConCat Lab