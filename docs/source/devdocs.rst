Developer documentation
-----------------------

The project follows fairly standard developer practices. Every new feature should be associated with a test, and every PR requires linting and formatting using ``ruff``.

Testing
```````
Tests are located in the ``tests`` folder of the repository, and are executed using ``pytest`` for every commit in every PR.

If a new test requires additional data (input files, schemas, etc.), they can be placed in a folder using the name of the test module (that is, ``test_drycal.py`` has its test files in ``test_drycal`` folder), or in the ``common`` folder for files that may be reused multiple times.

Formatting
``````````
All files should be formatted by ``ruff format``. Lines containing text fields, including docstrings, should be between 80-88 characters in length. Imports of functions should be absolute, that is including the ``yadg.`` prefix.


Implementing new features
``````````````````````````
**New extractors** should be implemented by:

- adding their schema into :class:`dgbowl_schemas.yadg.dataschema.DataSchema`
- adding their implementation in a separate Python package under :mod:`yadg.extractors`

Each extractor should be documented by adding a structured docstring at the top of the file. This documentation should describe the application and usage of the extractor, and refer to the Pydantic audotocs via :obj:`~dgbowl_schemas.yadg.dataschema` to discuss the features exposed via the parameters dictionary. If the filetype extracted is binary, a description of the file structure should be provided in the docstring. Every new filetype will have to be added into the :mod:`~dgbowl_schemas.yadg.dataschema.filetype` module as well.