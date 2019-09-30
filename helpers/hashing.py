import hashlib
import json

def hashfile(fn, method="sha1"):
    if method == "sha1":
        hasher = hashlib.sha1()
    elif method == "md5":
        hasher = hashlib.md5()
    with open(fn, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()
        
def hashobject(obj, method="sha1"):
    if method == "sha1":
        hasher = hashlib.sha1()
    elif method == "md5":
        hasher = hashlib.md5()
    hasher.update(json.dumps(obj, sort_keys=True).encode('utf-8'))
    return hasher.hexdigest()
