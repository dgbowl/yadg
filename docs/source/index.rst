**yadg**: yet another datagram
==============================

**yadg** is a set of tools and parsers aimed to process raw instrument data.

.. image:: images/schema_yadg_datagram.png
   :width: 600
   :alt: yadg is used to process raw data files using a DataSchema into a datagram.

Given an experiment represented by a `dataschema`, yadg will process the files 
and folders specified in each experimental `step` of the `dataschema`, and produce a
`datagram` -- a unified data structure containing all measured ("raw") data in a 
given experiment. 

The produced `datagram` is associated with full provenance info, and the data within
the `datagram` contains instrumental error estimates and is annotated with units.

.. admonition:: DEPRECATED in ``yadg-4.2``

   The post-processing features within ``yadg`` are deprecated as of ``yadg-4.2`` in 
   favour of the ``dgpost`` library, and will be completely removed in ``yadg-5.0``.

You can read more about yadg in our paper: [Kraus2022b]_.

.. toctree::
   :maxdepth: 1
   :caption: yadg user manual

   usage
   features
   citing

.. include:: parsers.rst

.. toctree::
   :maxdepth: 1
   :caption: yadg developer manual
   :hidden:

   devdocs
   version
   objects
   apidoc/yadg
