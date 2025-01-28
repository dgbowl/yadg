**yadg** version 6.1
````````````````````
.. warning::

   This version of yadg is not yet released.

..
  .. image:: https://img.shields.io/static/v1?label=yadg&message=v6.0&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/6.0
  .. image:: https://img.shields.io/static/v1?label=yadg&message=v6.0&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/6.0/
  .. image:: https://img.shields.io/static/v1?label=release%20date&message=2024-11-14&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-6.1`` are:


Breaking changes in ``yadg-6.1`` are:


Bug fixes in ``yadg-6.1`` include:

  - Fixed metadata extraction and added support for another version of the CVA technique in :mod:`yadg.extractors.eclab.mpr`. Thanks to `@acavell <https://github.com/acavell>`_ for providing test files.
  - Fixed timestamp parsing for D/M/Y formats of PicoVNA files in :mod:`yadg.extractors.touchstone.snp`.
