**yadg** version 7.0
````````````````````

..
   .. image:: https://img.shields.io/static/v1?label=yadg&message=v7.0&color=blue&logo=github
     :target: https://github.com/PeterKraus/yadg/tree/7.0
   .. image:: https://img.shields.io/static/v1?label=yadg&message=v7.0&color=blue&logo=pypi
     :target: https://pypi.org/project/yadg/7.0/
   .. image:: https://img.shields.io/static/v1?label=release%20date&message=2025-08-20&color=red&logo=pypi


Developed in the `ConCat Lab <https://tu.berlin/en/concat>`_ at Technische Universität Berlin (Berlin, DE).

New features in ``yadg-7.0`` are:

  - New uncertainty handling. Uncertainties for data are now stored as ``{val}_uncertainty`` instead of ``{val}_std_err``, and they are generally a single :class:`float` or :class:`int` per data variable. See the :ref:`Uncertainties <uncertainties-label>` section in the Features document. The change was motivated by the following issues:

    - The uncertainties, as stored in the ``NetCDF`` files produced in previous versions of :obj:`yadg`, were simply too large -- often inflating the size of the file by 100%, without adding much value.
    - The origin of the uncertainty was often unclear and certainly not machine-readable, so it was difficult to judge whether it should be trusted or not.
    - The suffix ``_std_err`` implied the uncertainty corresponds to the standard error of the data, this is however not true.

  - Support for Battery Capacity Determination (BCD) technique in :mod:`yadg.extractors.eclab.mpr` and :mod:`yadg.extractors.eclab.mpt`. Note that the ``Set I/C`` parameters in BCD are renamed to ``Set I/C 1`` and ``Set I/C 2`` in both :mod:`~yadg.extractors.eclab.mpr` and :mod:`~yadg.extractors.eclab.mpt` files. Thank you to `Joachim Laviolette <https://github.com/JL-CEA>`_ for providing test files.

  - Support for updating legacy yadg ``json`` *datagrams* in :mod:`yadg.extractors.yadg.json`. With this module, *datagrams* generated using ``yadg-4.x`` series can be updated to the new ``NetCDF`` format introduced in ``yadg-5.0``.

  - Support for extracting data from zip files containing known filetypes using ``yadg extract`` as well as :func:`yadg.extractors.extract`. More details are provided in :ref:`usage instructions<zip file extract>`. This also means that :mod:`yadg.extractors.fusion.zip` is not needed any more.


Breaking changes in ``yadg-7.0`` are:

  - The new uncertainty handling is a breaking change compared to :obj:`yadg-6.x`
  - For all extractors, the ``source`` (positional) argument now must be specified instead of ``fn`` or ``path``.
  - In :mod:`yadg.extractors.agilent.csv`, the ``signal`` data variable now has ``elution_time`` as a proper coordinate. Previously, the ``elution_time`` was expanded manually to the length of the largest trace present in the file, with ``np.nan`` used as padding for shorter traces. An arbitrary coordinate ``_`` was also present. Now, ``elution_time`` is expanded automatically by :func:`xarray.concat`, inserting ``np.nan`` into the ``signal`` data variable as necessary for ``elution_time`` which are not present in each trace.
  - In :mod:`yadg.extractors.touchstone.snp`, the acquisition parameters (S11, S21 etc.) are no longer NetCDF groups, but the label is prepended to the property name (e.g. ``S11/real`` is now ``S11_real``). This means the ``frequency`` coordinate is not duplicated.
  - In :mod:`yadg.extractors.fhimcpt.vna`, the schema now follows :mod:`~yadg.extractors.touchstone.snp` for consistency.

Bug fixes in ``yadg-7.0`` include:

  - The parameter ``Set I/C`` in :mod:`yadg.extractors.eclab.mpr` files should be ``C / N`` when set to 1, not ``C``.
  - Added columns 248 (``Rac``), 249 (``Rdc``), and 253 (``Acir od Dcir Control``) in :mod:`yadg.extractors.eclab.mpr` and :mod:`yadg.extractors.eclab.mpt`. Thanks to Muthu Vallinayagam from TU Freiberg for reporting the issue.
  - The command line argument ``--ignore-merge-errors`` was not being passed to the individual extractors when using the ``yadg extract`` syntax.
  - Fixed passing of :mod:`yadg.extractors.fusion.json` files where no species are present.
  - Fixed parsing of parameters in some :mod:`yadg.extractors.eclab.mpt` files, where "Cycle Definition" entry is missing.
  - The "Modify on" entries in :mod:`yadg.extractors.eclab.mpt` files are now properly processed, resulting in consistent parameters (or settings) with :mod:`yadg.extractors.eclab.mpr`, where only the last modification is stored.
