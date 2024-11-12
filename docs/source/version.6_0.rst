**yadg** version 6.0
``````````````````````
.. warning::

   This version of yadg is not yet released.

.. image:: https://img.shields.io/static/v1?label=yadg&message=v6.0&color=blue&logo=github
  :target: https://github.com/PeterKraus/yadg/tree/6.0
.. image:: https://img.shields.io/static/v1?label=yadg&message=v6.0&color=blue&logo=pypi
  :target: https://pypi.org/project/yadg/6.0/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=YYYY-MM-DD&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-6.0`` are:

  - Implemented support for merged/appended files in :mod:`yadg.extractors.eclab.mpr`. Test files taken from the data available at https://zenodo.org/doi/10.5281/zenodo.12165685. Thanks to Arnd Koeppe from KIT for bringing the issue up.
  - Implemented support for the Modular Potentio technique in :mod:`yadg.extractors.eclab.mpr`. Thanks to Graham Kimbell and Clea Burgel from Empa for providing test data.
  - Implemented support for the Constant Current and Constant Voltage techniques in :mod:`yadg.extractors.eclab.mpr`. Thanks to Carla Terboven from HZB for providing test data.

Other changes in ``yadg-6.0`` are:

  - As :class:`~xarray.DataTree` is now merged into the :mod:`xarray` module, ``yadg-6.0`` no longer depends on :mod:`xarray-datatree`.
  - The parameter specification within the ``original_metadata`` entries in :mod:`~yadg.extractors.eclab.mpr` should now be consistent with :mod:`~yadg.extractors.eclab.mpt`. Thanks to Carla Terboven from HZB for the contribution!
  - Support for ``python <= 3.9`` has been dropped.
  - Support for ``python == 3.13`` is now included.

Bug fixes in ``yadg-6.0`` include:

  - Increased supported I-range values in :mod:`yadg.extractors.eclab` up to 193.
  - Implemented support for a 33-parameter GCPL file in :mod:`yadg.extractors.eclab.mpr`.
  - Fixed parsing of optional metadata in :mod:`yadg.extractors.fusion.json`. Thanks to Emiliano Dal Molin for finding the bug and providing test data.
