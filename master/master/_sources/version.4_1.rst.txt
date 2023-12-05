**yadg** version 4.1.0
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.1.0&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/4.1.0
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.1.0&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/4.1.0/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2022-05-13&color=red&logo=pypi

Developed at Empa - Materials Science and Technology, in Dübendorf. 

New features since v4.0.0 are:

  - ability to archive raw data and reference the archive from within the `datagram`, 
    by using ``yadg preset --process --archive``
  - migrated `dataschema` validation from an in-house validation routine to a 
    Pydantic-based model, see :mod:`dgbowl_schemas.yadg`
  - added the :mod:`~yadg.parsers.xpstrace` parser with support for Panalytical files
  - added support for ``tomato.json`` filetypes to the :mod:`~yadg.parsers.electrochem` 
    and :mod:`~yadg.parsers.dummy` parsers
  - added support for ``fusion.zip`` filetypes to the :mod:`~yadg.parsers.chromtrace` parser

Bug fixes and other modifications include:

  - :mod:`yadg.parsers.chromtrace` format modified:
    
    - if peak integration data is present in the raw data file, this is now included
      in the ``"raw"`` key directly. The included quantities are ``height``, ``area``,
      ``concentration``, and ``xout`` for every detected species.
    - if peak integration is to be carried out by yadg, the resulting data is now
      available in the ``"derived"`` key directly. The included quantities are 
      ``height``, ``area``, ``concentration``, in addition to ``xout`` which was
      already part of the spec in v4.0.0.
    - peak integration is now more reliable by applying a threshold around zero
      for inflection point detection
  
  - :mod:`yadg.parsers.electrochem` format fixes:

    - the PEIS/GEIS data is split into timesteps, not cycles.
    - ``NaN`` and ``Inf`` in the metadata of some input formats should now be handled
      properly, without producing a non-compliant json file.
    - added partial support for ``mpr`` files including the ``ExtDev`` module


This project has received funding from the European Union’s Horizon 2020 research
and innovation programme under grant agreement No 957189. The project is part of
BATTERY 2030+, the large-scale European research initiative for inventing the
sustainable batteries of the future.

