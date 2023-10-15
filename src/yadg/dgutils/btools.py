import numpy as np
from typing import Union, Any


def read_pascal_string(pascal_bytes: bytes, encoding: str = "windows-1252") -> str:
    """Parses a length-prefixed string given some encoding.

    Parameters
    ----------
    bytes
        The bytes of the string starting at the length-prefix byte.

    encoding
        The encoding of the string to be converted.

    Returns
    -------
    str
        The string decoded from the input bytes.

    """
    mul = 2 if encoding in {"utf-16"} else 1
    lstr = int.from_bytes(pascal_bytes[0:1], byteorder="big") * mul
    if len(pascal_bytes) < lstr + 1:
        raise ValueError("Insufficient number of bytes.")
    string_bytes = pascal_bytes[1 : lstr + 1]
    return string_bytes.decode(encoding)


def read_value(
    data: bytes,
    offset: int,
    dtype: Union[np.dtype, str],
    encoding: str = "windows-1252",
) -> Any:
    """Reads a single value or a set of values from a buffer at a certain offset.

    Just a handy wrapper for np.frombuffer(..., count=1) With the added benefit of
    allowing the 'pascal' keyword as an indicator for a length-prefixed
    string.

    The read value is converted to a built-in datatype using
    np.dtype.item().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.

    offset
        Start reading the buffer from this offset (in bytes).

    dtype
        Data-type to read in.

    encoding
        The encoding of the bytes to be converted.

    Returns
    -------
    Any
        The unpacked and converted value from the buffer.

    """
    if dtype == "pascal":
        # Allow the use of 'pascal' in all of the dtype maps.
        return read_pascal_string(data[offset:], encoding="windows-1252")
    elif dtype in {"utf-8", "utf-16"}:
        return read_pascal_string(data[offset:], encoding=dtype)
    value = np.frombuffer(data, offset=offset, dtype=dtype, count=1)
    item = value.item()
    if value.dtype.names:
        item = [i.decode(encoding) if isinstance(i, bytes) else i for i in item]
        return dict(zip(value.dtype.names, item))
    return item.decode(encoding) if isinstance(item, bytes) else item
