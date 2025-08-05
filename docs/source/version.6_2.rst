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

  - The control column name in :mod:`yadg.extractors.eclab.mpr` is now ``control_V or I``, with appropriate units. The previous ``control_I`` and ``control_V`` columns are **not** created if not present in the ``mpr`` files.

  - The control columns in :mod:`yadg.extractors.eclab.mpt` have changed, as usually all three columns are present (originally titled as ``control/V/mA``, ``control/V`` as well as ``control/I``). The ``control/V/mA`` column is now converted by yadg to ``control_V or I`` with appropriate units, this is the column used for consistency checking. Note that there is often an off-by-one difference in the values of ``control/V/mA`` and ``control/I`` in the ``mpt`` files.

Bug fixes in ``yadg-next`` include:

  - Fixed metadata extraction in :mod:`yadg.extractors.eclab.mpt` where ``control_V or I`` column would not match that present in the corresponding ``mpr`` files.
  - Fixed metadata extraction in :mod:`yadg.extractors.eclab.mpt` so that multiple ``Comments:`` lines are concatenated instead of just the last line being kept.
  - Added further ``Set I/C`` parameters and fixed the assignment into ``control_V or I`` columns. Thanks to `@Locki3 <https://github.com/Locki3>`_ for providing test files.
  - Fixed ``param format`` and ``data_column`` in CV files generated with EC-Lab version 11.50 using the :mod:`yadg.extractors.eclab.mpr` module. Thank you to J.N. Hausmann from Helmholtz-Zentrum Berlin für Materialien und Energie for providing the test files.
  - Fixed parsing of various kinds of Modulo Bat files in :mod:`yadg.extractors.eclab.mpr`. Thank you to `@JohannesBaller <https://github.com/JohannesBaller>`_ for providing test files.
  - Columns in :mod:`yadg.extractors.eclab.mpr` files may have different meanings based on which other columns are also present in the files, see `issue 225 <https://github.com/dgbowl/yadg/issues/225>`_. Added a (hopefully extensible) way to tackle such conflicts and clarified the warnings.
