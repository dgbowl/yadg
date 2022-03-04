**yadg** version 4.1.0
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.0.1&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/4.0.1
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.0.1&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/4.0.1/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2022-02-14&color=red&logo=pypi

Developed at Empa - Materials Science and Technology, in Dübendorf. 

New features since v4.0.0 are:

  - ``chromtrace`` format modified:
    
    - if peak integration data is present in the raw data file, this is now included
      in the ``"raw"`` key directly. The included quantities are ``height``, ``area``,
      ``concentration``, and ``xout`` for every detected species.
    - if peak integration is to be carried out by **yadg**, the resulting data is now
      available in the ``"derived"`` key directly. The included quantities are 
      ``height``, ``area``, ``concentration``, in addition to ``xout`` which was
      already part of the spec in v4.0.0.
  
  - ``electrochemistry`` format fixes:

    - the PEIS/GEIS data is split into timesteps, not cycles. This change has been 
      introduced in v4.0.1
    - ``NaN`` and ``Inf`` in the metadata of some input formats should now be handled
      properly, without producing a non-compliant json file.
    - added partial support for ``mpr`` files including ``ExtDev`` module
      
  - ``chromtrace`` supports ``fusion.zip`` format