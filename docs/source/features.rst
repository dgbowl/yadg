Key features of **yadg**
------------------------

Units and uncertainties
```````````````````````
One of the key features of **yadg** is the enforced association of units and uncertainties with measured properties. This means that all experimental quantities are accompanied by an uncertainty estimate, derived either from the (``string -> float``) representation of the data, or from instrumental resolution, if known.

Units
+++++
**yadg** relies on the |pint|_ package for storing units in the created `datagrams`. For this, an extended :class:`pint.UnitRegistry` is exposed in **yadg**, containing definitions of some quantities present in the raw data files in addition to |pint|'s standard unit registry. This :class:`pint.UnitRegistry` should be used in downstream packages
which depend on **yadg**.

In the resulting |NetCDF| files, the unit annotations are stored in ``.attrs["units"]`` on each :class:`xr.DataArray`, that is within each "column" of each "node" of the :class:`datatree.DataTree`. If an entry does not contain ``.attrs["units"]``, the quantity is dimensionless. See :mod:`yadg.dgutils.pintutils` for more info.

Uncertainties
+++++++++++++
In many cases it is possible to define more than one uncertainty for each measurement: for example, accuracy, precision, as well as instrument resolution etc. may be available. The convention in **yadg** is that when both a measure of within-measurement uncertainty (resolution) and a cross-measurement error (accuracy) are available, the stored uncertainty corresponds to the instrumental resolution associated with each datapoint. The accuracy of the measurement (which is normally a higher value than that of the resoution)
can be obtained using post-processing, e.g. as a ``mean()`` and ``stdev()`` of a series of data.

Unless more information is available, when converting :class:`str` data to :class:`float`, the uncertainty is determined from the last significant digit specified in the :class:`str`. For this, the functionality from within the |uncertainties|_ package is used.

In the resulting |NetCDF| files, the uncertainties for each ``f"{entry}"`` are stored as a separate data variable, ``f"{entry}_std_err"``. The link between the nominal value and its uncertainty is annotated using ``.attrs["ancillary_variables"] = f"{entry}_std_err"``. The reverse link between the uncertainty and its nominal value is annotated similarly, using ``.attrs["standard_name"] = f"{entry} standard_error"``. This follows the `NetCDF CF Metadata Conventions <https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html>`_, see `Section 3.4 on Ancillary Data <https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#ancillary-data>`_.


Timestamping
````````````
Another key feature in **yadg** is the timestamping of all datapoints. The Unix timestamp is used, as it's the natural timestamp for Python, and with its resolution in seconds it can be easily converted to minutes or hours.

Most of the supported file formats contain a timestamp of some kind. However, several file formats may not define both date and time of each datapoint, or may define neither. That is why **yadg** includes a powerful "external date" interface, see :func:`~yadg.dgutils.dateutils.complete_timestamps`.


`Dataschema` validation
```````````````````````
Additionally, **yadg** provides `dataschema` validation functionality, by using the schema models from the :mod:`dgbowl_schemas.yadg_dataschema` package, implemented in |Pydantic|_. The schemas are developed in lockstep with **yadg**. This |Pydantic|-based validator class should be used to ensure that the incoming `dataschema` is valid.


.. _pint: https://pint.readthedocs.io/en/stable/

.. |pint| replace:: **pint**

.. _uncertainties: https://pythonhosted.org/uncertainties/

.. |uncertainties| replace:: **uncertainties**

.. _Pydantic: https://pydantic-docs.helpmanual.io/

.. |Pydantic| replace:: **Pydantic**

.. |NetCDF| replace:: ``NetCDF``