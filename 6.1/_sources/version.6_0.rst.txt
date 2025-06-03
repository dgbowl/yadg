**yadg** version 6.0
````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v6.0&color=blue&logo=github
  :target: https://github.com/PeterKraus/yadg/tree/6.0
.. image:: https://img.shields.io/static/v1?label=yadg&message=v6.0&color=blue&logo=pypi
  :target: https://pypi.org/project/yadg/6.0/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2024-11-14&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-6.0`` are:

  - Implemented support for merged/appended files in :mod:`yadg.extractors.eclab.mpr`. Test files taken from the data available at https://zenodo.org/doi/10.5281/zenodo.12165685. Thanks to Arnd Koeppe from KIT for bringing the issue up.
  - Implemented support for the Modular Potentio technique in :mod:`yadg.extractors.eclab.mpr`. Thanks to Graham Kimbell and Clea Burgel from Empa for providing test data.
  - Implemented support for the Constant Current and Constant Voltage techniques in :mod:`yadg.extractors.eclab.mpr`. Thanks to Carla Terboven from HZB for providing test data.

Breaking changes in ``yadg-6.0`` are:

  - As :class:`~xarray.DataTree` is now merged into the :mod:`xarray` module, ``yadg-6.0`` no longer depends on :mod:`xarray-datatree`. For data stored |NetCDF| files, this shouldn't be a problem, as they can be read using :func:`xarray.open_datatree`. However, if you stored a :class:`datatree.DataTree` as a ``pickle``, and attempt to load it using :class:`xarray.DataTree`, this may not work!
  - The parameter specification within the ``original_metadata`` entries in :mod:`~yadg.extractors.eclab.mpr` should now be consistent with :mod:`~yadg.extractors.eclab.mpt`. This means renaming of most parameters in :mod:`~yadg.extractors.eclab.mpr` to match :mod:`~yadg.extractors.eclab.mpt`, and a much larger parameter map to map from the :class:`int` values stored in :mod:`~yadg.extractors.eclab.mpr` files to their :class:`str` counterparts. Thanks to Carla Terboven from HZB for the contribution!
  - Support for ``python <= 3.9`` has been dropped. This is a consequence of ``yadg-6.0`` requiring ``xarray >= 2024.10.0``. However, support for ``python == 3.13`` is now included.

Bug fixes in ``yadg-6.0`` include:

  - Increased supported I-range values in :mod:`yadg.extractors.eclab` up to 193.
  - Implemented support for a 33-parameter GCPL file in :mod:`yadg.extractors.eclab.mpr`.
  - Fixed parsing of optional metadata in :mod:`yadg.extractors.fusion.json`. Thanks to Emiliano Dal Molin for finding the bug and providing test data.

.. |NetCDF| replace:: ``NetCDF``