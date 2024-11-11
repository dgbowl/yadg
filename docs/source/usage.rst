.. _usage:

How to use **yadg**
===================
We have prepared an interactive, Binder-compatible Jupyter notebook, showing the installation and example usage of **yadg**. The latest version of the notebook and the direct link to Binder are:

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6351210.svg
    :target: https://doi.org/10.5281/zenodo.6351210
.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/zenodo/10.5281/zenodo.6351210/?labpath=index.ipynb

There are two main ways of using **yadg**:

#. A limited `extractor` mode, useful to extract (meta)-data from individual files.
#. A fully featured `parser` mode, intended to process all files semantically related to a single "experiment". This mode requires a `dataschema`.

.. _extractor mode:

`Extractor` mode
----------------
In this mode, **yadg** can be invoked by providing just the `FileType` and the path to the input file:

.. code-block:: bash

    yadg extract filetype infile [outfile]

The ``infile`` will be then parsed using **yadg** into a :class:`~xarray.DataTree`, and, if successful, saved as a |NetCDF|_ file, optionally using the specified ``outfile`` location. In addition to any ``original_metadata`` stored in the ``.attrs`` object of the resulting :class:`~xarray.DataTree`, it will contain **yadg**-specific metadata, including the annotation of provenance (i.e. ``yadg extract``), `filetype` information, and the resolved defaults of `timezone`, `locale`, and `encoding` used to create it.

.. warning::

    By default, in `extractor` mode, **yadg** assumes the following defaults:

        - `timezone` is set to the ``localtime`` of the `localhost`,
        - `locale` is set to the default ``LC.NUMERIC`` locale of the `localhost`,
        - `encoding` of the input files is set to ``UTF-8`` or the `extractor` default.

    All of the above options might lead to improper parsing of the input files. While errors due to improper `encoding` are likely to be immediately obvious as they lead to crashes; `locale` errors might only be obvious upon inspection of data (e.g. data parsed using wrong decimal separators); and incorrect `timezone` information may lead to errors that are much more subtle. You can specify the correct values for these three parameters, if known, on the command line using:

    .. code-block:: bash

        yadg extract --locale=de_DE --encoding=utf-8 --timezone=Europe/Berlin filetype infile [outfile]


Metadata-only extraction
````````````````````````
To use **yadg** to extract and retrieve just the metadata contained in the input file, pass the ``--meta-only`` argument:

.. code-block:: bash

    yadg extract --meta-only filetype infile

The metadata are returned as a ``.json`` file, and are generated using the :func:`~xarray.Dataset.to_dict` function of :class:`xarray.Dataset`. They contain a description of the data coordinates (``coords``), dimensions (``dims``), and variables (``data_vars``), and include their names, attributes, dtypes, and shapes.

The list of supported `filetypes` that can be extracted using **yadg** can be found in the left sidebar. For more information about the `extractor` concept, see the |datatractor|_ project.

.. _parser mode:

`Parser` mode
-------------
The main purpose of **yadg** is to process a bunch of raw data files according to a provided `dataschema` into well-defined, annotated, FAIR-data |NetCDF|_ files. To use **yadg** like this, it should be invoked as follows:

.. code-block:: bash

    yadg process infile [outfile]

Where ``infile`` corresponds to the ``json`` or ``yaml`` file containing the `dataschema`, and the optional ``outfile`` is the filename to which the created :class:`~xarray.DataTree` should be saved (it defaults to ``datagram.nc``).

In this fully-featured usage pattern via `dataschema`, the individual `extractors` can be further configured and combined. The currently implemented `extractors` are documented in the sidebar.

`Dataschema` from presets
`````````````````````````
This alternative form of using **yadg** in `parser` mode is especially useful when processing data organised in a consistent folder structure between several experimental runs. The user should prepare a `preset` file, which then gets patched to a `dataschema` file using the provided folder path:

.. code-block:: bash

    yadg preset infile folder [outfile]

Where ``infile`` is the `preset`, ``folder`` is the folder path for which the `preset` should be modified, and the optional ``outfile`` is the filename to which the created `dataschema` should be saved.

Alternatively, if the `dataschema` should be processed immediately, the ``--process`` (or ``-p``) switch can be used with the following usage pattern:

.. code-block:: bash

    yadg preset -p infile folder [outfile.nc]

This syntax will process the created `dataschema` immediately, and the :class:`~xarray.DataTree` will be saved to ``outfile.nc`` instead.

Finally, the raw data files in the processed ``folder`` can be archived, checksumed, and referenced in the :class:`~xarray.DataTree`, by using the following pattern:

.. code-block:: bash

    yadg preset -p -a infile folder [outfile.nc]

This will create a |NetCDF|_ file in ``outfile.nc`` as well as a ``outfile.zip`` archive including the whole contents of the specified ``folder``.

`Dataschema` version updater
````````````````````````````
If you'd like to update a `dataschema` from a previous version of **yadg** to the current latest one, use the following syntax:

.. code-block:: bash

    yadg update infile [outfile]

This will update the `dataschema` specified in ``infile`` and save it to ``outfile``, if provided.


.. _NetCDF: https://www.unidata.ucar.edu/software/netcdf/

.. _datatractor: https://github.com/datatractor

.. |NetCDF| replace:: ``NetCDF``

.. |datatractor| replace:: Datatractor