**yadg** version 4.0.0
``````````````````````


A major rewrite of **yadg**. The code includes documentation, test suite, and is tested
using CI.

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

  - large updates to older parsers:

    - ``chromtrace``: an updated, unified chromatography trace parser. The trace 
      integration routine has been completely re-written. The parser now supports
      multiple formats, including binary Agilent ``.ch`` and ``.dx``, and Fusion
      ``.json`` format in addition to the formats previously supported by ``gctrace``.
    - ``qftrace``: updated with several bug fixes and performance improvements, 
      no longer using :class:`(np.matrix)`.

  - a consistent interface for supplying calibration data
  - versioning of `datagrams` as well as update pathways from older `schema` files
  - `schema` preset functionality, for routine applications of **yadg** to structured
    raw data archives
  - `externaldate` functionality for completing and/or replacing deduced timestamps
    using external sources in a unified fashion
