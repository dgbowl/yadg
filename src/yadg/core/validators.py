import logging
from typing import Union

from .. import core
from ..dgutils import ureg

logger = logging.getLogger(__name__)


def _list_validator(l: list) -> bool:
    if len(l) == 3:
        return _float_list(l)
    else:
        return _general_list(l)


def _float_list(l: list) -> bool:
    if isinstance(l[0], float) and isinstance(l[1], float) and isinstance(l[2], str):
        logger.warning("Old [float, float, str] syntax detected.")
        return True
    else:
        return _general_list(l)


def _general_list(l: list) -> bool:
    for v in l:
        if isinstance(v, list):
            return _list_validator(v)
        elif isinstance(v, dict):
            return _dict_validator(v)
        else:
            assert isinstance(v, str) or isinstance(v, int), (
                f"List elements have to be one of [str, int, dict, list], "
                f"but entry id:{l.index(v)}:{type(v)} is neither: {l}"
            )
    return True


def _unit_validator(u: str) -> bool:
    assert u in ureg, f"unit {u} is not defined."
    return True


def _dict_validator(d: dict) -> bool:
    for k, v in d.items():
        if k in ["n", "s", "u"] and len({"n", "s", "u"}.intersection(d.keys())) == 3:
            if k in ["n", "s"] and isinstance(v, (float, list)):
                pass
            elif k == "u" and isinstance(v, str):
                assert _unit_validator(v)
            else:
                logger.error("We shouldn't be here: %s", f"{k=}, {v=}")
                return False
        elif isinstance(v, float):
            assert k == "uts", f"Only 'uts' can be a float entry, not '{k}'."
        elif isinstance(v, list):
            assert _list_validator(v)
        elif isinstance(v, dict):
            assert _dict_validator(v)
        else:
            assert isinstance(v, str) or isinstance(v, int), (
                f"Dict elements have to be one of [str, int, dict, list], "
                f"but '{k}':{type(v)} is neither: {v}"
            )
    return True


def validator(item: Union[list, dict, str], spec: dict) -> True:
    """
    Worker validator function.

    This function checks that ``item`` matches the specification supplied in ``spec``.
    The ``spec`` :class:`(dict)` can have the following entries:

    - ``"type"`` :class:`(type)`, a required entry, defining the type of ``item``,
    - ``"all"`` :class:`(dict)` defining a set of required keywords and their respective ``spec``,
    - ``"any"`` :class:`(dict)` defining a set of optional keywords and their respective ``spec``,
    - ``"one"`` :class:`(dict)` defining a set of mutually exclusive keywords and their respective ``spec``,
    - ``"each"`` :class:`(dict)` providing the ``spec`` for any keywords not listed in ``"all"``, ``"any"``, or ``"one"``,
    - ``"allow"`` :class:`(bool)` a switch whether to allow unspecified keys.

    To extend the existing `datagram` and `schema` specs, look into :mod:`yadg.core.spec_datagram`
    and :mod:`yadg.core.spec_schema`, respectively.

    Parameters
    ----------
    item
        The ``item`` to be validated.

    spec
        The ``spec`` with which to validate the ``item``

    Returns
    -------
    True: bool
        If the ``item`` matches the ``spec``, returns `True`. Otherwise, an `AssertionError` is raised.
    """
    assert isinstance(item, spec["type"]), (
        f"Item '{item}' does not match prescribed type " f"in spec '{spec['type']}'."
    )
    if len({"all", "one", "any", "each"}.intersection(spec)) > 0 and spec["type"] in [
        list,
        dict,
    ]:
        for k, v in spec.get("all", {}).items():
            assert k in item, (
                f"Required entry '{k}' was not specified " f"in item '{item}'."
            )
        if "one" in spec:
            initem = set(spec["one"]).intersection(item)
            assert len(initem) == 1, (
                f"Exactly one of entries in {spec['one']} has to be "
                f"provided in item {item}, but {len(initem)} were provided: {initem}."
            )
        for k in item:
            s = False
            for d in ["all", "one", "any"]:
                if k in spec.get(d, []):
                    s = d
            assert s or spec.get("allow", False) or "each" in spec, (
                f"Key '{k}' in item {item} " f"is not understood."
            )
            if s:
                assert validator(item[k], spec[s][k])
            elif "each" in spec:
                if spec["type"] == list:
                    assert validator(k, spec["each"])
                else:
                    assert validator(item[k], spec["each"])
    elif len({"all", "one", "any"}.intersection(spec)) > 0 and spec["type"] in [str]:
        if "all" in spec:
            assert (
                len(spec["all"]) == 1 and item in spec["all"]
            ), f"Item '{item}' is not in {spec['all']}."
        if "one" in spec:
            assert item in spec["one"], f"Item '{item}' is not in {spec['one']}."
        if "any" in spec:
            assert item in spec["any"], f"Item '{item}' is not in {spec['any']}."
    return True


def validate_datagram(datagram: dict) -> True:
    """
    Datagram validator.

    Checks the overall `datagram` format against the `datagram` spec, and ensures that
    each floating-point value is accompanied by standard deviation and unit.

    The current `datagram` specification is:

    -  The `datagram` must be a :class:`(dict)` with two entries:

       - ``"metadata"`` :class:`(dict)`: A top-level entry containing metadata.
       - ``"steps"`` :class:`(list[dict])`: List corresponding to a sequence of `steps`.

    - The ``"metadata"`` entry has to contain information about the ``"provenance"`` of
      the `datagram`, the creation date using ISO8601 format in ``"date"`` :class:`(str)`
      entry, a full copy of the input `schema` in the ``"input_schema"`` entry, and
      version information in ``"datagram_version"`` :class:`(str)`.

    - Each element in the ``"steps"`` corresponds to a single `step` from the `schema`.
    - Each `step` in ``"steps"`` has to contain a ``"metadata"`` :class:`(dict)` entry,
      and a ``"data"`` :class:`(list)`; an optional ``"common"`` :class:`(dict)` data
      block can be provided.
    - Each timestep in the ``"data"`` list has to specify a timestamp using the
      Unix Timestamp format in ``"uts"`` :class:`(float)` entry; the original filename
      in ``"fn"`` :class:`(str)` entry. The raw data present in this original filename
      is stored as sub-entries within the ``"raw"`` :class:`(dict)` entry. Any derived
      data, such as that obtained via calibration, integration, or fitting, has to be
      stored in the ``"derived"`` :class:`(dict)`.

    .. note::
        A floating-point entry should always have its standard deviation specified.
        Internal processing of this data is always carried out using the :class:`(ufloat)`
        type, which ought to be exported as a ``{"n": value, "s": std_dev, "u": "-"}`` keypair.

    .. note::
        Most numerical data should have associated units. The validator expects all
        floating-point entries to be in a ``{"n": value, "s": std_dev}`` format for
        properties with an arbitrary unit, and ``{"n": value, "s": std_dev, "u": unit}``
        for properties with a defined unit.

    Parameters
    ----------
    datagram
        The `datagram` to be validated.

    Returns
    -------
    True: bool
        If the `datagram` passes all assertions, returns `True`. Else, an `AssertionError` is raised.
    """
    # datagram has to meet the spec
    assert validator(datagram, core.spec_datagram.datagram)
    # validate each step in the datagram
    for step in datagram["steps"]:
        assert all(
            ["fn" in ts for ts in step["data"]]
        ), "The 'fn' entry has to be provided in each timestep."
        for ts in step["data"]:
            assert _dict_validator(ts)
    return True
