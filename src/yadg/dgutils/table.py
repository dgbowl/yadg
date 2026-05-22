from babel.numbers import parse_decimal
from decimal import Decimal
from typing import Callable


def process_row(
    items: list[str],
    locale: str = "en_GB",
) -> tuple[float, type, int, int]:
    vals = []
    kind = []
    digs = []
    exps = []
    for item in items:
        try:
            dec = parse_decimal(item, locale=locale)
            dtp = dec.as_tuple()
            if "e" in item or "E" in item:
                kind.append(float)
                vals.append(float(dec))
            elif dtp.exponent == 0:
                kind.append(int)
                vals.append(int(dec))
            else:
                vals.append(float(dec))
                kind.append(Decimal)
            digs.append(len(dtp.digits))
            exps.append(dtp.exponent)
        except ValueError:
            if item == "":
                vals.append(float("nan"))
                kind.append(int)
                digs.append(0)
                exps.append(0)
            else:
                vals.append(item)
                kind.append(str)
                digs.append(None)
                exps.append(None)
    return vals, kind, digs, exps


def process_table(
    lines: list[str],
    headers: list[str],
    sep: str = None,
    strip: str = None,
    locale: str = "en_GB",
    uncertainties: bool = True,
    uncertainties_int_columns: bool = True,
    datecolumns: list[int] = None,
    datefunc: Callable = None,
) -> dict:
    """
    A function for parsing a list of string values, containing numerical data, into a dict
    structure that can be used to construct a xr.Dataset.

    Parameters
    ----------
    lines
        The list of individual records.

    headers
        The list of headers for those records. If there are more items in each line than they are headers,
        the rightmost columns will be dropped.

    sep
        The separator character ("," or ";") used to split the line into items. Defaults to whitespace.

    strip
        A set of extra characters to be stripped from each item.

    locale
        The locale of the data, defaults to "en_GB".

    uncertainties
        A :class:`bool` triggering whether uncertainties should be processed. Defaults to ``True``.

    datecolumns
        A list of column indices which will be used to construct a ``uts``. Those columns won't be treated as data.

    datefunc
        A :class:`Callable`, using which the items identified in ``datecolumns`` will be processed into ``uts``.

    Returns
    -------
    data_vars
        A :class:`dict` structured in order to construct a :class:`xarray.Dataset` via :func:`xarray.Dataset.from_dict`.

    """

    vals = {k: [] for k in headers}
    types = {k: int for k in headers}
    precs = {k: 0 for k in headers}
    if datecolumns is not None:
        uts = []

    for line in lines:
        parts = [i.strip().strip(strip) for i in line.split(sep)]
        if datecolumns is not None:
            uts.append(datefunc(*[parts[i] for i in datecolumns]))
        vs, ts, ds, es = process_row(parts, locale)
        for i, (k, v, t, d, e) in enumerate(zip(headers, vs, ts, ds, es)):
            if datecolumns is not None and i in datecolumns:
                continue
            vals[k].append(v)
            if uncertainties is False:
                continue
            if types[k] is int:
                types[k] = t
            elif types[k] is Decimal and t is not int:
                types[k] = t
            if t is str:
                continue
            elif t in (int, Decimal):
                if e in {"n", "F"}:
                    e = 0
                prec = abs(e)
            else:
                prec = d
            precs[k] = max(precs[k], prec)

    data_vars = {}

    for i, k in enumerate(headers):
        if datecolumns is not None and i in datecolumns:
            continue
        data_vars[k] = {
            "dims": ("uts",) if datecolumns is not None else (k,),
            "data": vals[k],
            "attrs": {},
        }

        if types[k] is str:
            continue
        if types[k] is int and uncertainties_int_columns is False:
            continue
        if uncertainties is False:
            continue

        ku = f"{k.replace(' ', '_')}_uncertainty"
        data_vars[k]["attrs"]["ancillary_variables"] = ku
        data_vars[ku] = {
            "dims": (ku,),
            "data": [precs[k] if types[k] is float else 10 ** (-precs[k])],
            "attrs": {
                "standard_name": f"{k} standard_error",
                "standard_error_multiplier": 1,
                "yadg_uncertainty_type": "sig" if types[k] is float else "abs",
                "yadg_uncertainty_distribution": "rectangular",
                "yadg_uncertainty_source": "str_conv",
            },
        }
    if datecolumns is not None:
        data_vars["uts"] = {
            "dims": ("uts",),
            "data": uts,
        }
    return data_vars
