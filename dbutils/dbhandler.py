from pymongo import MongoClient
import json
import numpy as np

_VERSION = 0.1

def _connect(dbparams):
    client = MongoClient(dbparams["url"], dbparams["port"])
    db = client[dbparams["db"]]
    return client, db

def store(document,dbparams):
    client, db = _connect(dbparams)
    samehash = db.collection.find_one({"metadata.hash": document["metadata"]["hash"]})
    if samehash == None:
        result = db.collection.insert_one(document)
        print(f'DBUTILS: stored a document with hash {document["metadata"]["hash"][:10]} under ID {result.inserted_id}')
        retid = result.inserted_id
    else:
        print(f'DBUTILS: found 1 document with hash {document["metadata"]["hash"][:10]} under ID {samehash["_id"]}')
        retid = samehash["_id"]
    return retid

def load(value, dbparams, keytype="_id"):
    client, db = _connect(dbparams)
    result = db.collection.find_one({keytype: value})
    print(f'DBUTILS: found a document with {{{keytype}: {value}}} under ID {result["_id"]}')
    return result
