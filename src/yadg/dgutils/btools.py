import numpy as np
from io import BufferedIOBase
from typing import Union, Any


def old_read_from_file(
    f: BufferedIOBase, offset: int, dtype: str, count: int = 1
) -> Union[str, np.ndarray]:
    f.seek(offset)
    if dtype == "utf-8":
        len = int.from_bytes(f.read(1), byteorder="big")
        chars = f.read(len)
        return chars.decode("utf-8")
    elif dtype == "utf-16":
        len = int.from_bytes(f.read(1), byteorder="big") * 2
        chars = f.read(len)
        return chars.decode("utf-16")
    elif count == 1:
        return np.fromfile(f, offset=0, dtype=dtype, count=1)[0]
    else:
        return np.fromfile(f, offset=0, dtype=dtype, count=count)


def old_read_from_buffer(
    buf: bytes, offset: int, dtype: str, count: int = 1
) -> Union[str, np.ndarray]:
    if dtype == "utf-8":
        len = int.from_bytes(buf[offset:offset], byteorder="big")
        chars = buf[offset + 1 : offset + 1 + len]
        return chars.decode("utf-8")
    elif dtype == "utf-16":
        len = int.from_bytes(buf[offset:offset], byteorder="big") * 2
        chars = buf[offset + 1 : offset + 1 + len]
        return chars.decode("utf-16")
    elif count == 1:
        return np.frombuffer(buf, offset=offset, dtype=dtype, count=1)[0]
    else:
        return np.frombuffer(buf, offset=offset, dtype=dtype, count=count)


def old_read_value(
    object: Union[BufferedIOBase, bytes], offset: int, dtype: str, count: int = 1
) -> Union[str, np.ndarray, int, float]:
    if isinstance(object, bytes):
        return read_from_buffer(object, offset, dtype, count)
    else:
        return read_from_file(object, offset, dtype, count)


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
    if len(pascal_bytes) < pascal_bytes[0] + 1:
        raise ValueError("Insufficient number of bytes.")
    string_bytes = pascal_bytes[1 : pascal_bytes[0] + 1]
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
        return read_pascal_string(data[offset:])
    value = np.frombuffer(data, offset=offset, dtype=dtype, count=1)
    item = value.item()
    if value.dtype.names:
        item = [i.decode(encoding) if isinstance(i, bytes) else i for i in item]
        return dict(zip(value.dtype.names, item))
    return item.decode(encoding) if isinstance(item, bytes) else item


def read_values(
    data: bytes, offset: int, dtype: Union[np.dtype, str], count: int
) -> list:
    """Reads in multiple values or sets of values from a buffer starting at offset.

    Just a handy wrapper for np.frombuffer() with count >= 1.

    The read values are converted to a list of built-in datatypes using
    np.ndarray.tolist().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.

    offset
        Start reading the buffer from this offset (in bytes).

    dtype
        Data-type to read in.

    count
        Number of items to read. -1 means all data in the buffer.

    Returns
    -------
    Any
        The values read from the buffer as specified by the arguments.

    """
    values = np.frombuffer(data, offset=offset, dtype=dtype, count=count)
    if values.dtype.names:
        return [dict(zip(value.dtype.names, value.item())) for value in values]
    # The ndarray.tolist() method converts numpy scalars to built-in
    # scalars, hence not just list(values).
    return values.tolist()
