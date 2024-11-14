.. _installation:

How to install **yadg**
=======================
**yadg** is available on the `Python Package Index <https://pypi.org/project/yadg/>`_, which means the latest stable version can be installed using ``pip``:

.. code-block:: bash

    pip install yadg

To install the latest development version of **yadg**, which is available on `the project GitHub <https://github.org/dgbowl/yadg>`, you can use the ``git+https://`` installation path:

.. code-block:: bash

    pip install git+https://github.org/dgbowl/yadg.git

Finally, **yadg** supports editable installations. If you want to access the test suite, the easiest way to install **yadg** would be to clone the GitHub repository, install **yadg** in editable mode with ``[testing]`` optional dependencies, and run the test suite via ``pytest``:

.. code-block:: bash

    git clone https://github.org/dgbowl/yadg.git
    cd yadg
    pip install -e .[testing]
    pytest -vvx
