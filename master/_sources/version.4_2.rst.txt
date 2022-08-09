**yadg** version 4.2
``````````````````````

.. warning::

  ``yadg-4.2`` is not yet released.

.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.2&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/4.2
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.2&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/4.2/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2022-05-13&color=red&logo=pypi

Developed at Empa - Materials Science and Technology, in Dübendorf. 

New features since v4.1 are:

  - :mod:`~yadg.parsers.chromdata` parser for parsing integrated chromatography data,
  

Bug fixes and other modifications include:

  - the ``drycal`` filetypes in :mod:`yadg.parsers.flowdata` should now work for 
    overnight experiments;
  - the :mod:`~yadg.parsers.chromtrace` parser now focuses on parsing chromatography
    traces only, with trace integration deprecated in favour of ``dgpost``;
  - the :mod:`~yadg.parsers.flowdata` parser now no longer creates a default ``"flow"``
    entry in derived data;
  - the ``calfile`` and ``calib`` parameters have been deprecated in favour of ``dgpost``;
  - the metadata in :mod:`~yadg.parsers.chromdata` and :mod:`~yadg.parsers.chromtrace`
    was modified to only include true metadata as opposed to sample data;


    