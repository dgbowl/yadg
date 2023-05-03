**yadg** version 3.1.0
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v3.1.0&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/3.1.0
.. image:: https://img.shields.io/static/v1?label=yadg&message=v3.1.0&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/3.1.0/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2021-09-11&color=red&logo=pypi

First released version of **yadg**, containing functionality developed at the
Fritz Haber Institute in Berlin. Design ideas, decisions, and workflow described in
[Kraus2022a]_.

Major features are:

  - **yadg** is now a python package
  - ``gctrace``: support for gas-phase chromatrography, including:

    - trace integration,
    - EZChrom ASCII export format,
    - CHROMTAB ASCII export format,

  - ``qftrace``: support for reflection trace measurements, including:

    - fitting of quality factor using Lorentzian and naive methods
    - fitting of quality factor using Kajfez's circle fitting method [Kajfez1994]_

  - ``meascsv``: support for in-house MCPT logger for flow and temperature data
