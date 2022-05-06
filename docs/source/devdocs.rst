Developer documentation
-----------------------

The project follows fairly standard developer practices. Every new feature should be
associated with a test, and every PR should be formatted using automated formatter.

Testing
```````
Tests are located in the ``tests`` folder of the repository, and are executed using
``pytest`` for every commit in every PR. 

If a new test requires additional data (input files, schemas, etc.), they can be 
placed in a folder using the name of the test module (that is, ``test_drycal.py`` has 
its test files in ``test_drycal`` folder), or in the ``common`` folder for files
that may be reused multiple times.

Several convenience functions are provided in the ``utils.py`` module:

  - ``datadir``, implementing the above mentioned external test data functionality,
  - ``datagram_from_input``, wrapping a simple :class:`(dict)`-based input for tests 
    into a `schema`, that is then parsed into a `datagram`
  - ``standard_datagram_test``, which checks the validity of the returned `datagram`
  - ``compare_result_dicts``, which compares a reference dictionary in the 
    ``{"n": float, "s": float, "u": str}`` format with that in a `datagram`

Formatting
``````````
All files should be formatted by ``black``. Lines containing text fields, including 
docstrings, should be between 80-88 characters in length. Imports of functions should 
be absolute, that is including the ``yadg.`` prefix.


Implementing new parsers
````````````````````````
New parsers should be implemented by:

- adding their schema into :class:`~dgbowl_schemas.yadg.DataSchema`
- adding their implementation in a separate Python package under :mod:`yadg.parsers`

Generally, specific filetype parsers should be kept separate from the main parser
function in the module.


Documentation
`````````````
Each parser should be documented by adding a structured docstring into the 
``__init__.py`` file of each parser module. This documentation should describe the 
application and usage of the parser, and refer to the Pydantic audotocs via 
:class:`~dgbowl_schemas.yadg.DataSchema` to discuss the features exposed via the
parameters dictionary. Finally, a short summary of the quantities provided in the 
``"raw"`` and ``"derived"`` entries should be included, and whether any 
``"metadata"`` are exposed.

Each file type of each parser should be documented as a top-level docstring in the 
relevant module. If the file is binary, a description of the file structure should
be provided in the docstring.