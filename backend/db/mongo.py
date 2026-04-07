import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database


_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_db() -> Database:
    global _client, _db
    if _db is not None:
        return _db

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "invoice_platform")

    _client = MongoClient(mongo_uri)
    _db = _client[db_name]
    return _db


def get_invoices_collection():
    return get_db()["invoices"]


def get_runs_collection():
    return get_db()["runs"]
