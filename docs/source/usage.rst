Program usage
-------------

`Schema` processing
```````````````````

The basic usage of **yadg** is to process a `schema` to a `datagram`. For this,
the program should be invoked as follows:

.. code-block:: bash

    yadg infile [outfile]

Where ``infile`` corresponds to the `schema` json file, and the optional ``outfile``
is the filename to which the created `datagram` should be saved (defaults to
``datagram.json``).