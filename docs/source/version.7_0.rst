**yadg** version next
`````````````````````

..
   .. image:: https://img.shields.io/static/v1?label=yadg&message=v6.2&color=blue&logo=github
     :target: https://github.com/PeterKraus/yadg/tree/6.2
   .. image:: https://img.shields.io/static/v1?label=yadg&message=v6.2&color=blue&logo=pypi
     :target: https://pypi.org/project/yadg/6.2/
   .. image:: https://img.shields.io/static/v1?label=release%20date&message=2025-08-20&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-next`` are:

  - Support for Battery Capacity Determination (BCD) technique in :mod:`yadg.extractors.eclab.mpr` and :mod:`yadg.extractors.eclab.mpt`. Note that the ``Set I/C`` parameters in BCD are renamed to ``Set I/C 1`` and ``Set I/C 2`` in both :mod:`~yadg.extractors.eclab.mpr` and :mod:`~yadg.extractors.eclab.mpt` files. Thank you to `Joachim Laviolette <https://github.com/JL-CEA>`_ for providing test files.

Breaking changes in ``yadg-next`` are:

  - In :mod:`yadg.extractors.agilent.csv`, the ``signal`` data variable now has ``elution_time`` as a proper coordinate. Previously, the ``elution_time`` was expanded manually to the length of the largest trace present in the file, with ``np.nan`` used as padding for shorter traces. An arbitrary coordinate ``_`` was also present. Now, ``elution_time`` is expanded automatically by :func:`xarray.concat`, inserting ``np.nan`` into the ``signal`` data variable as necessary for ``elution_time``s which are not present in each trace.

Bug fixes in ``yadg-next`` include:

  - The parameter ``Set I/C`` in :mod:`yadg.extractors.eclab.mpr` files should be ``C / N`` when set to 1, not ``C``.

