**yadg** version 4.2
``````````````````````
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.2&color=blue&logo=github
    :target: https://github.com/PeterKraus/yadg/tree/4.2
.. image:: https://img.shields.io/static/v1?label=yadg&message=v4.2&color=blue&logo=pypi
    :target: https://pypi.org/project/yadg/4.2/
.. image:: https://img.shields.io/static/v1?label=release%20date&message=2022-08-29&color=red&logo=pypi

Developed at Empa - Materials Science and Technology, in Dübendorf. 

New features since v4.1 are:

  - a new :mod:`~yadg.parsers.chromdata` parser for parsing post-processed chromatography data,
  - the :mod:`~yadg.parsers.basiccsv` parser has an additional parameter ``strip``, allowing
    the user to strip extra characters (such as ``"`` or ``'``) from column headers and data,
  - :mod:`yadg` will now warn you if a newer version is available on PyPI.

Backwards-incompatible changes include:

  - the :mod:`~yadg.parsers.chromtrace` parser now focuses on parsing chromatography
    traces only, use :mod:`~yadg.parsers.chromdata` for parsing post-processed chromatographic
    data; 
  - the :mod:`~yadg.parsers.flowdata` parser now no longer creates a default ``"flow"``
    entry in derived data;  
  - data post-processing within :mod:`yadg`, including chromatographic trace integration,
    reflection coefficient processing, and calibration functionality is deprecated in favour 
    of ``dgpost``.
  
Bug fixes include:

  - the :func:`~yadg.parsers.basiccsv.process_row` from the :mod:`~yadg.parsers.basiccsv`
    parser now handles empty cells by creating sparse `datagrams`;
  - the ``drycal`` filetypes in :mod:`~yadg.parsers.flowdata` should now work for 
    overnight experiments;
  - the metadata in :mod:`~yadg.parsers.chromdata` and :mod:`~yadg.parsers.chromtrace`
    was modified to only include true metadata as opposed to sample data;
  - the :mod:`~yadg.parsers.electrochem` parser now allows for toggling the transposing
    of PEIS/GEIS traces.


This project has received funding from the European Union’s Horizon 2020 research
and innovation programme under grant agreement No 957189. The project is part of
BATTERY 2030+, the large-scale European research initiative for inventing the
sustainable batteries of the future.
    
