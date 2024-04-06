**yadg** version 5.1
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v5.1&color=blue&logo=github
  :target: https://github.com/PeterKraus/yadg/tree/5.1
.. image:: https://img.shields.io/static/v1?label=yadg&message=v5.1&color=blue&logo=pypi
  :target: https://pypi.org/project/yadg/5.1/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2024-XX-YY&color=red&logo=pypi


Developed in the |concat_lab|_ at Technische Universität Berlin (Berlin, DE).

New features since ``yadg-5.0`` are:

  - Support for Touchstone ``.sNp`` files using the :mod:`yadg.extractors.touchstone.snp` extractor. Test files are truncated to first 100 lines, they were obtained from the following DOIs:
    - ``Device_r_*um.s1p`` from https://zenodo.org/doi/10.5281/zenodo.7850136
    - ``SCENARIO*_pulserside_30k_3G.s1p`` from https://zenodo.org/doi/10.5281/zenodo.10016477
    - ``CABLE_3_5MM_1N_TYPE_CONNECTORS.S2P`` from https://zenodo.org/doi/10.5281/zenodo.10016477
    - ``Fig8_*cm.s1p`` from https://zenodo.org/doi/10.5281/zenodo.10222705
    - ``VNA_radial_middle.s*p`` from https://zenodo.org/doi/10.5281/zenodo.7339709


Other changes in ``yadg-5.1`` are:

  - The dataschema has been simplified, eliminating parsers in favour of extractors.
  - The code has been reorganised to highlight the extractor functionality in favour of parsers.


.. _concat_lab: https://tu.berlin/en/concat

.. |concat_lab| replace:: ConCat Lab