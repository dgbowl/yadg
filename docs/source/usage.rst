How to use **yadg**
===================
We have prepared an interactive, Binder-compatible Jupyter notebook, showing the installation and example usage of yadg. The latest version of the notebook and the direct link to Binder are:

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6351210.svg
    :target: https://doi.org/10.5281/zenodo.6351210
.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/zenodo/10.5281/zenodo.6351210/?labpath=index.ipynb

There are two main ways of using **yadg**:

#. A limited `extractor` mode, useful to extract (meta)-data from single, separate files.
#. A fully featured `parser` mode, requiring a `dataschema`, intended to process all files semantically related to a single "experiment".

`Extractor` mode
----------------

.. warning::

    The `extractor` mode has been introduced in ``yadg-5.0`` and its API is not yet stable.

The option to use **yadg** as an `extractor` comes as a consequence of the `MaRDA Metadata Extractors WG <https://github.com/marda-alliance/metadata_extractors>`_. In this mode, **yadg** can be invoked by providing just the `FileType` and the path to the input file:

.. code-block:: bash

    yadg extract filetype infile [outfile]

The ``infile`` will be then parsed using **yadg** and, if successful, saved as a |NetCDF|_ file, optionally using the specified ``outfile`` location.

.. warning::

    In `extractor` mode, **yadg** assumes the following defaults:

    - `timezone` is set to the ``localtime`` of the `localhost`,
    - `locale` is set to the default ``LC.NUMERIC`` locale of the `localhost`,
    - `encoding` of the input files is set to ``UTF-8`` or the `extractor` default.

    All of the above options might lead to improper parsing of the input files. Errors due to improper `locale` might be obvious (e.g. data parsed using wrong decimal separators); incorrect `timezone` information may lead to errors that are more subtle.

The resulting NetCDF files will contain annotation of provenance (i.e. ``yadg extract``), `filetype` information, and the resolved defaults of `timezone`, `locale`, and `encoding` used to create the NetCDF file.

The list of supported `filetypes` that can be extracted using **yadg** can be found in the left sidebar.

`Parser` mode
-------------
The main purpose of yadg is to process a bunch of raw data files according to a provided `dataschema` into a well-defined, annotated, FAIR-data file called `datagram`. As of ``yadg-5.0``, the `datagram` is stored in |NetCDF|_ files. To use **yadg** like this, it should be invoked as follows:

.. code-block:: bash

    yadg process infile [outfile]

Where ``infile`` corresponds to the ``json`` or ``yaml`` file containing the `dataschema`, and the optional ``outfile`` is the filename to which the created `datagram` should be saved (it defaults to ``datagram.nc``).

In this fully-featured usage pattern via `dataschema`, **yadg** offloads the responsibility of data extraction and normalisation to its modules, called `parsers`. The currently implemented `parsers` are documented in the sidebar.

`Dataschema` from presets
+++++++++++++++++++++++++
This alternative form of using **yadg** in `parser` mode is especially useful when processing data organised in a consistent folder structure between several experimental runs. The user should prepare a `preset` file, which then gets patched to a `dataschema` file using the provided folder path:

.. code-block:: bash

    yadg preset infile folder [outfile]

Where ``infile`` is the `preset`, ``folder`` is the folder path for which the `preset` should be modified, and the optional ``outfile`` is the filename to which the created `dataschema` should be saved.

Alternatively, if the `dataschema` should be processed immediately, the ``--process`` (or ``-p``) switch can be used with the following usage pattern:

.. code-block:: bash

    yadg preset -p infile folder [outfile.json]

This syntax will process the created `dataschema` immediately, and the `datagram` will be saved to ``outfile.json`` instead.

Finally, the raw data files in the processed ``folder`` can be archived, checksumed, and referenced in the `datagram`, by using the following pattern:

.. code-block:: bash

    yadg preset -p -a infile folder [outfile.json]

This will create a `datagram` in ``outfile.json`` as well as a ``outfile.zip`` archive from the whole contents of the specified ``folder``.

`Dataschema` version updater
++++++++++++++++++++++++++++
If you'd like to update a `dataschema` from a previous version of yadg to the current latest one, use the following syntax:

.. code-block:: bash

    yadg update infile [outfile]

This will update the `dataschema` specified in ``infile`` and save it to ``outfile``, if provided.


.. _NetCDF: https://www.unidata.ucar.edu/software/netcdf/

.. |NetCDF| replace:: ``NetCDF``
