**yadg** version 7.x
````````````````````
..
    .. image:: https://img.shields.io/static/v1?label=yadg&message=v7.0&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/7.0
    .. image:: https://img.shields.io/static/v1?label=yadg&message=v7.0&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/7.0/
    .. image:: https://img.shields.io/static/v1?label=release%20date&message=2026-07-18&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-7.x`` are:

  - Added support for the CPW technique in :mod:`yadg.extractors.eclab` module. Thank you to `Franz Pichler <https://github.com/mathcodemaster>`_ for sharing a test file.
  - Significant speed-up for :mod:`yadg.extractors.eclab` extractors by reworking `param` look-up (`#271 <https://github.com/dgbowl/yadg/pull/271>`_).
  - Significant speed-up for all extractors relying on :func:`yadg.dgutils.table.process_table` by processing the supplied locale only once per call and not on every row  (`#271 <https://github.com/dgbowl/yadg/pull/271>`_).

..
  Breaking changes in ``yadg-7.x`` are:

  Bug fixes in ``yadg-7.x`` include:
