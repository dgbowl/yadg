**yadg** usage
--------------

`Schema` processing
```````````````````
The basic usage of **yadg** is to process a `schema` to a `datagram`. For this,
the program should be invoked as follows:

.. code-block:: bash

    yadg process infile [outfile]

Where ``infile`` corresponds to the `schema` json file, and the optional ``outfile``
is the filename to which the created `datagram` should be saved (defaults to
``datagram.json``).

`Schema` from presets
`````````````````````
This alternative usage of **yadg** is especially useful to process data organised in 
consistent folder structures between experimental runs. The user should prepare a 
`preset` file, which then gets patched to a `schema` file using a provided folder path:

.. code-block:: bash

    yadg preset infile folder [outfile]

Where ``infile`` is the `preset`, ``folder`` is the folder path for which the `preset`
should be modified, and the optional ``outfile`` is the filename to which the created
`schema` should be saved.

Alternatively, if the `schema` is to be processed immediately, the ``--process`` (or
``-p``) switch can be used according to the following usage pattern:

.. code-block:: bash

    yadg preset -p infile folder [outfile]

This syntax will process the created `schema` immediately, and the `datagram` will be 
saved to ``outfile`` instead.

Version updater
```````````````
If you'd like to update a `schema` (or a `datagram`) from previous versions of yadg to
the current one, use the following syntax:

.. code-block:: bash

    yadg update schema infile [outfile]

This will update the `schema` specified in ``infile``, also parsing old calibration
files, if findable. Updating of `datagrams` is possible, but not recommended, unless
the raw data files are not available. We strongly recommend either updating a `schema`
and re-processing the raw data, or updating a `datagram` and extracting the new `schema`
from within.
