**yadg** version next
`````````````````````
..
  .. image:: https://img.shields.io/static/v1?label=yadg&message=v6.1&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/6.1
  .. image:: https://img.shields.io/static/v1?label=yadg&message=v6.1&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/6.1/
  .. image:: https://img.shields.io/static/v1?label=release%20date&message=2025-06-03&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-next`` are:


Breaking changes in ``yadg-next`` are:

  - Some column names in :mod:`yadg.extractors.eclab.mpr` files might have changed, as EC-Lab 11.62 has a new naming convention for derived quantities. In particular:

    - ``Energy charge`` is now ``Energy we charge``,
    - ``Energy discharge`` is now ``Energy we discharge``,
    - ``P`` is now ``Pwe``,
    - ``R`` is now ``Rwe``.

    This will also unfortunately affect processing older ``mpr`` files. Depending on which version of EC-Lab was used to convert the ``mpr`` file to the ``mpt`` file, the ``mpt`` file will contain the old (i.e. ``P`` or ``Energy charge``) or the new (i.e. ``Pwe`` or ``Energy we charge``) column names. For yadg internal consistency testing, we still attempt an exact match between ``mpr`` and ``mpt`` columns; if the ``mpr`` column is not present in the ``mpt`` file, we look for an equivalent column without the ``we`` annotation.

  - The ``control/V/mA`` column and the ``mode`` column in :mod:`~yadg.extractors.eclab.mpr` as well as :mod:`~yadg.extractors.eclab.mpr` files is now used to create the ``control_V`` (units ``V``) and ``control_I`` (units ``mA``) columns in both kinds of files:

    - The original ``control/V`` and ``control/mA`` which are present in ``mpt`` and may be present in ``mpr`` files are now overwritten by values from the ``control/V/mA`` column, which is always present.
    - In any given row, either ``control_V`` or ``control_I`` is set, with the other (non-controlling) column being ``np.nan``.
    - The currently known ``mode`` values correspond to:

      - ``1`` for constant current (``control_I`` = limiting value)
      - ``2`` for constant voltage (``control_V`` = limiting value)
      - ``3`` for open circuit (``control_I`` = forced to zero)

    Thanks to `Graham Kimbell <https://github.com/g-kimbell>`_ from Empa for helping out with these changes.

Bug fixes in ``yadg-next`` include:

  - Fixed metadata extraction in :mod:`yadg.extractors.eclab.mpt` so that multiple ``Comments:`` lines are concatenated instead of just the last line being kept.
  - Added further ``Set I/C`` parameters. Thanks to `@Locki3 <https://github.com/Locki3>`_ for providing test files.
  - Fixed ``param format`` and ``data_column`` in CV files generated with EC-Lab version 11.50 using the :mod:`yadg.extractors.eclab.mpr` module. Thank you to J.N. Hausmann from Helmholtz-Zentrum Berlin für Materialien und Energie for providing the test files.
  - Fixed parsing of various kinds of Modulo Bat files in :mod:`yadg.extractors.eclab.mpr`. Thank you to `Johannes Baller <https://github.com/JohannesBaller>`_ for providing test files.
  - Fixed parsing of missing columns in GCPL files in :mod:`yadg.extractors.eclab.mpr`. Thank you to `Joachim Laviolette <https://github.com/JL-CEA>`_ for providing test files.
  - Columns in :mod:`yadg.extractors.eclab.mpr` files may have different meanings based on which other columns are also present in the files, see `issue 225 <https://github.com/dgbowl/yadg/issues/225>`_. Added a (hopefully extensible) way to tackle such conflicts and clarified the warnings.
  - It looks like there are only 256 columns in :mod:`~yadg.extractor.eclab.mpr` files, with higher IDs corresponding to ``id % 256`` in all cases. Thanks to `Graham Kimbell <https://github.com/g-kimbell>`_ for first pointing this out.
