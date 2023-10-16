Developer documentation
-----------------------

The project follows fairly standard developer practices. Every new feature should be associated with a test, and every PR requires linting using ``flake8`` and formatting using ``black``.

Testing
```````
Tests are located in the ``tests`` folder of the repository, and are executed using ``pytest`` for every commit in every PR.

If a new test requires additional data (input files, schemas, etc.), they can be placed in a folder using the name of the test module (that is, ``test_drycal.py`` has its test files in ``test_drycal`` folder), or in the ``common`` folder for files that may be reused multiple times.

Formatting
``````````
All files should be formatted by ``black``. Lines containing text fields, including docstrings, should be between 80-88 characters in length. Imports of functions should be absolute, that is including the ``yadg.`` prefix.


Implementing new features
``````````````````````````
**New parsers** should be implemented by:

- adding their schema into :class:`dgbowl_schemas.yadg.dataschema.DataSchema`
- adding their implementation in a separate Python package under :mod:`yadg.parsers`

Each `parser` should be documented by adding a structured docstring into the ``__init__.py`` file of each new sub-module of :mod:`yadg.parsers`. This documentation should describe the application and usage of the `parser`, and refer to the Pydantic audotocs via :class:`~dgbowl_schemas.yadg.dataschema.DataSchema` to discuss the features exposed via the parameters dictionary. Generally, code implementing the parsing of specific `filetypes` should be kept separate from the main `parser` function in the module.

**New filetypes** should be implemented as sub-modules of their `parser`. They should be documented using a top-level docstring in the relevant sub-module. If the `filetype` is binary, a description of the file structure should be provided in the docstring. Every new `filetype` will have to be added into the :mod:`~dgbowl_schemas.yadg.dataschema.filetype` module as well.

**New extractors** can be registered using a shim in the :mod:`yadg.extractors` module, referring to the `filetype`. The ``__init__.py`` of each `extractor` should expose:

- an :func:`extract` function which returns an :class:`xarray.Dataset`,
- a :class:`set` named :obj:`supports`, enumerating all `filetypes` that can be extracted by the new `extractor.`

Note that a new `extractor` requires its `filetype` to be added in the :mod:`~dgbowl_schemas.yadg.dataschema.filetype` module as well.