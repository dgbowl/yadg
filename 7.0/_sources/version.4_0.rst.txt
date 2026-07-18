**yadg** version 4.0.1
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.0.1&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/4.0.1
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.0.1&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/4.0.1/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2022-02-14&color=red&logo=pypi

A major rewrite of **yadg**. Developed at Empa - Materials Science and Technology, in 
Dübendorf. The code includes documentation, test suite, and is tested using CI. This 
version has been published in JOSS [Kraus2022b]_.

Major features are:

  - validation of `schemas` and `datagrams`
  - uncertainties and units for all measured quantities stored by default and enforced
    by the validators
  - raw data is now retained by default and separated from derived data
  - several new parsers, including:

    - ``electrochemistry``: a parser for electrochemistry data, currently supporting
      BioLogic cyclers via binary ``.mpr`` and text ``.mpt`` files generated in EC-Lab.
      Supports standard methods as well as impedance spectroscopy traces (PEIS, GEIS)
      and complex methods (MB).
    - ``masstrace``: a parser for mass spectroscopy data, supporting binary Quadstar 
      ``.sac`` files.
    - ``basiccsv``: a tabulated data parser, with row processing written for modular
      use in other parsers
    - ``xpstrace``: a parser for x-ray photoelectron spectroscopy data, supporting
      ULVAC PHI Multipak XPS traces (.spe)

  - large updates to older parsers:

    - ``chromtrace``: an updated, unified chromatography trace parser. The trace 
      integration routine has been completely re-written. The parser now supports
      multiple formats, including binary Agilent ``.ch`` and ``.dx``, and Fusion
      ``.json`` format in addition to the formats previously supported by ``gctrace``.
    - ``qftrace``: updated with several bug fixes and performance improvements, 
      no longer using :class:`(np.matrix)`.

Other, minor features include:

  - a consistent interface for supplying calibration data
  - versioning of `datagrams` as well as update pathways from older `schema` files
  - `schema` preset functionality, for routine applications of **yadg** to structured
    raw data archives
  - `externaldate` functionality for completing and/or replacing deduced timestamps
    using external sources in a unified fashion
  - validation of units present in the `datagrams`

New in version 4.0.1:

  - fixed accuracy of phase in electrochemistry files to 1°.
  - fixed splitting of GEIS/PEIS traces in a single file into multiple timesteps


This project has received funding from the European Union’s Horizon 2020 research
and innovation programme under grant agreement No 957189. The project is part of
BATTERY 2030+, the large-scale European research initiative for inventing the
sustainable batteries of the future.

