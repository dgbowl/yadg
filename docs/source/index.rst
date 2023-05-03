**yadg**: yet another datagram
==============================
.. image:: https://badgen.net/badge/docs/dgbowl.github.io/grey?icon=firefox
   :target: https://dgbowl.github.io/yadg
.. image:: https://badgen.net/pypi/v/yadg/?icon=pypi
   :target: https://pypi.org/project/yadg
.. image:: https://badgen.net/github/tag/dgbowl/yadg/?icon=github
   :target: https://github.com/dgbowl/yadg
.. image:: https://github.com/dgbowl/yadg/actions/workflows/codeql.yml/badge.svg?branch=master
   :target: https://github.com/dgbowl/yadg/actions/workflows/codeql.yml

**yadg** is a set of tools and parsers aimed to process raw instrument data.

.. image:: images/schema_yadg_datagram.png
   :width: 600
   :alt: yadg is used to process raw data files using a datadchema into a NetCDF datagram.

Given an experiment represented by a `dataschema`, **yadg** will process the files and folders specified in each experimental `step` of the `dataschema`, and produce a `datagram` -- a unified data structure containing all measured ("raw") data in a given experiment. As of ``yadg-5.0``, the `datagram` is stored as a |NetCDF|_ file. The produced `datagram` is associated with full provenance info, and the data within the `datagram` contain instrumental error estimates and are annotated with units.

You can read more about **yadg** in our paper: [Kraus2022b]_.

.. note::

   The post-processing features within **yadg** have been deprecated in ``yadg-4.2`` and removed in ``yadg-5.0``. If you are looking for a post-processing library, have a look at |dgpost|_ instead.


.. toctree::
   :maxdepth: 1
   :caption: yadg user manual
   :hidden:

   usage
   features
   citing

.. include:: parsers.rst

.. include:: extractors.rst

.. toctree::
   :maxdepth: 1
   :caption: yadg developer manual
   :hidden:

   devdocs
   version
   objects
   apidoc/yadg

.. _NetCDF: https://www.unidata.ucar.edu/software/netcdf/

.. _dgpost: https://dgbowl.github.io/dgpost

.. |NetCDF| replace:: ``NetCDF``

.. |dgpost| replace:: **dgpost**