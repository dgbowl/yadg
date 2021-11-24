import numpy as np
from io import BufferedIOBase
from typing import Union


def read_from_file(
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


def read_from_buffer(
    buf: bytes, offset: int, dtype: str, count: int = 1
) -> Union[str, np.ndarray]:
    if dtype == "utf-8":
        len = int.from_bytes(buf[offset], byteorder="big")
        chars = buf[offset + 1 : offset + 1 + len]
        return chars.decode("utf-8")
    elif dtype == "utf-16":
        len = int.from_bytes(buf[offset], byteorder="big") * 2
        chars = buf[offset + 1 : offset + 1 + len]
        return chars.decode("utf-16")
    elif count == 1:
        return np.frombuffer(buf, offset=offset, dtype=dtype, count=1)[0]
    else:
        return np.frombuffer(buf, offset=offset, dtype=dtype, count=count)


def read_value(
    object: Union[BufferedIOBase, bytes], offset: int, dtype: str, count: int = 1
) -> Union[str, np.ndarray, int, float]:
    if isinstance(object, bytes):
        return read_from_buffer(object, offset, dtype, count)
    else:
        return read_from_file(object, offset, dtype, count)
