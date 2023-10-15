**yadg**: yet another datagram
==============================
.. image:: https://badgen.net/badge/docs/dgbowl.github.io/grey?icon=firefox
   :target: https://dgbowl.github.io/yadg
.. image:: https://badgen.net/pypi/v/yadg/?icon=pypi
   :target: https://pypi.org/project/yadg
.. image:: https://badgen.net/github/tag/dgbowl/yadg/?icon=github
   :target: https://github.com/dgbowl/yadg

**yadg** is a set of tools and parsers aimed to process raw instrument data. Given an experiment represented by a `dataschema`, **yadg** will process the files and folders specified in this `dataschema`, and produce a `datagram`, which is a unified data structure containing all measured ("raw") data in a given experiment. The `parsers` available in **yadg** are shown in the sidebar. As of ``yadg-5.0``, the `datagram` is stored as a |NetCDF|_ file. The produced `datagram` is associated with full provenance info, and the data within the `datagram` contain instrumental error estimates and are annotated with units. You can read more about **yadg** in our paper: [Kraus2022b]_.


.. image:: images/schema_yadg_datagram.png
   :width: 600
   :alt: yadg is used to process raw data files using a datadchema into a NetCDF datagram.


Some of the **yadg** parsers are exposed via an `extractor` interface, allowing the user to extract (meta)-data from individual files without requiring a `dataschema`. Several file formats are supported, as shown in the sidebar. You can read more about this `extractor` interface on the |marda_extractors|_ website, as well as in the :ref:`Usage: Extractor mode<extractor mode>` section of this documentation.

.. warning::

   All of the post-processing features within **yadg** have been removed in ``yadg-5.0``, following their deprecation in ``yadg-4.2``. If you are looking for a post-processing library, have a look at |dgpost|_ instead.


Contributors
````````````
- `Peter Kraus <https://github.com/PeterKraus>`_
- `Nicolas Vetsch <https://github.com/vetschn>`_

Acknowledgements
````````````````
This project has received funding from the following sources:

- European Union’s Horizon 2020 programme under grant agreement ID `957189 <https://cordis.europa.eu/project/id/957189>`_.
- DFG's Emmy Noether Programme under grant number `490703766 <https://gepris.dfg.de/gepris/projekt/490703766?language=en>`_.

The project is also part of BATTERY 2030+, the large-scale European research initiative for inventing the sustainable batteries of the future.


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

.. _marda_extractors: https://github.com/marda-alliance/metadata_extractors

.. |NetCDF| replace:: ``NetCDF``

.. |dgpost| replace:: **dgpost**

.. |marda_extractors| replace:: MaRDA Metadata Extractors WG