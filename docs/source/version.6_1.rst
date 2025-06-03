**yadg** version 6.1
````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v6.1&color=blue&logo=github
  :target: https://github.com/PeterKraus/yadg/tree/6.1
.. image:: https://img.shields.io/static/v1?label=yadg&message=v6.1&color=blue&logo=pypi
  :target: https://pypi.org/project/yadg/6.1/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2025-06-03&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-6.1`` are:

  - Added support for extraction from different sources rather than just files.

    - Extraction from a :class:`bytes` object can be requested using :func:`yadg.extractors.extract_from_bytes`.
    - Currently, this is only implemented for :mod:`yadg.extractors.eclab.mpr`, which can now extract either :class:`Path` or :class:`bytes` objects.
    - Thanks to `@carla-terboven <https://github.com/carla-terboven>`.

Breaking changes in ``yadg-6.1`` are:

  - The :func:`extract` function of each ``Extractor`` module now expects a positional :obj:`source` argument instead of a required keyword argument :obj:`fn`. The internal ``Extractor`` API has changed in the following way:

    - Passing :obj:`fn` to ``Extractors`` is deprecated and will stop working in a future version of :mod:`yadg`.
    - If an extraction from a file is requested, :class:`Path` **must** now be passed as :obj:`source`.
    - An extraction from another object type can be implemented by registering a dispatch function for that type in each ``Extractor``.

    Note that the :func:`yadg.extractors.extract` function still requests the usual two arguments, i.e. an :obj:`filename: str` and :obj:`path: Path | str`. The new behaviour does not affect this high-level external API.

Bug fixes in ``yadg-6.1`` include:

  - Fixed metadata extraction and added support for another version of the CVA technique in :mod:`yadg.extractors.eclab.mpr`. Thanks to `@acavell <https://github.com/acavell>`_ for providing test files.
  - Fixed timestamp parsing for D/M/Y formats of PicoVNA files in :mod:`yadg.extractors.touchstone.snp`.
  - Fixed issue when the filename was passed to :mod:`yadg.extractors.touchstone.snp` as :class:`Path` instead of :class:`str`.
