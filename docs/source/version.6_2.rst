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


Bug fixes in ``yadg-next`` include:

  - Fixed metadata extraction in :mod:`yadg.extractors.eclab.mpt` where ``control_*`` columns would not match the names present in the corresponding ``mpr`` files.
  - Fixed metadata extraction in :mod:`yadg.extractors.eclab.mpt` so that multiple ``Comments:`` lines are concatenated instead of just the last line being kept.
  - Added further ``Set I/C`` parameters. Thanks to `@Locki3 <https://github.com/Locki3>`_ for providing test files.
  - Fixed ``param format`` and ``data_column`` in CV files generated with EC-Lab version 11.50 using the :mod:`yadg.extractors.eclab.mpr` module. Thank you to J.N. Hausmann from Helmholtz-Zentrum Berlin für Materialien und Energie for providing the test files.
  - Fixed parsing of various kinds of Modulo Bat files in :mod:`yadg.extractors.eclab.mpr`. Thank you to `Johannes Baller <https://github.com/JohannesBaller>`_ for providing test files.
  - Fixed parsing of missing columns in GCPL files in :mod:`yadg.extractors.eclab.mpr`. Thank you to `Joachim Laviolette <https://github.com/JL-CEA>`_ for providing test files.
  - Columns in :mod:`yadg.extractors.eclab.mpr` files may have different meanings based on which other columns are also present in the files, see `issue 225 <https://github.com/dgbowl/yadg/issues/225>`_. Added a (hopefully extensible) way to tackle such conflicts and clarified the warnings.
