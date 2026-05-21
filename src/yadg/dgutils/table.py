from babel.numbers import parse_decimal
from decimal import Decimal


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
            vals.append(float(dec))
            dtp = dec.as_tuple()
            if "e" in item or "E" in item:
                kind.append(float)
            elif dtp.exponent == 0:
                kind.append(int)
            else:
                kind.append(Decimal)
            digs.append(len(dtp.digits))
            exps.append(dtp.exponent)
        except ValueError:
            vals.append(item)
            kind.append(str)
            digs.append(None)
            exps.append(None)
    return vals, kind, digs, exps


def process_table(
    lines: list[str],
    headers: list[str],
    sep: str = None,
    locale: str = "en_GB",
    uncertainties: bool = True,
) -> dict:
    """
    A function for parsing a list of string values, containing numerical data, into a xr.Dataset
    including determining uncertainties.
    """

    vals = {k: [] for k in headers}
    types = {k: int for k in headers}
    precs = {k: 0 for k in headers}

    for line in lines:
        vs, ts, ds, es = process_row(line.split(sep), locale)
        for k, v, t, d, e in zip(headers, vs, ts, ds, es):
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
                prec = abs(e)
            else:
                prec = d
            precs[k] = max(precs[k], prec)

    data_vars = {}

    for k in headers:
        data_vars[k] = {
            "dims": (k,),
            "data": vals[k],
            "attrs": {},
        }

        if types[k] is str:
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
    return data_vars
