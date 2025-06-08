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
  - Added further ``Set I/C`` parameters. Thanks to `@Locki3 <https://github.com/Locki3>`_ for providing test files.
