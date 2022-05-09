How to use **yadg**
-------------------
We have prepared an interactive, Binder-compatible Jupyter notebook, showing the 
installation and example usage of yadg. The latest version of the notebook and 
the direct link to Binder are:

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6351210.svg
    :target: https://doi.org/10.5281/zenodo.6351210
.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/zenodo/10.5281/zenodo.6351210/?labpath=index.ipynb


`Dataschema` processing
```````````````````````
The basic purpose of yadg is to process a bunch of raw data files according to a
provided `dataschema` into a well-defined, annotated, FAIR-data file called `datagram`. 
To use yadg like this, it should be invoked as follows:

.. code-block:: bash

    yadg process infile [outfile]

Where ``infile`` corresponds to the `dataschema` json file, and the optional 
``outfile`` is the filename to which the created `datagram` should be saved 
(defaults to ``datagram.json``).

`Dataschema` from presets
`````````````````````````
This alternative form of using yadg is especially useful when processing data organised 
in a consistent folder structure between several experimental runs. The user should 
prepare a `preset` file, which then gets patched to a `dataschema` file using the 
provided folder path:

.. code-block:: bash

    yadg preset infile folder [outfile]

Where ``infile`` is the `preset`, ``folder`` is the folder path for which the `preset`
should be modified, and the optional ``outfile`` is the filename to which the created
`dataschema` should be saved.

Alternatively, if the `dataschema` should be processed immediately, the ``--process`` 
(or ``-p``) switch can be used with the following usage pattern:

.. code-block:: bash

    yadg preset -p infile folder [outfile.json]

This syntax will process the created `dataschema` immediately, and the `datagram` will 
be saved to ``outfile.json`` instead.

Finally, the raw data files in the processed ``folder`` can be archived, checksumed,
and referenced in the `datagram`, by using the following pattern:

.. code-block:: bash

    yadg preset -p -a infile folder [outfile.json]

This will create a `datagram` in ``outfile.json`` as well as a ``outfile.zip`` archive
from the whole contents of the specified ``folder``.

Version updater
```````````````
If you'd like to update a `dataschema` from a previous version of yadg to the current 
latest one, use the following syntax:

.. code-block:: bash

    yadg update schema infile [outfile]

This will update the `dataschema` specified in ``infile``, also parsing old calibration
files, if findable. 

.. warning::
    
    Updating of `datagrams` is possible, but not recommended, unless the raw data files 
    are not available. We strongly recommend updating a `dataschema` and re-processing 
    the raw data.
