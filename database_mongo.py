from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

_client = MongoClient(MONGO_URI)
db = _client[MONGO_DB]

def insert_comment(document: dict):
    """document ex: {produto_id: 1, cliente_id: 5, comentario: "...", data: datetime}"""
    return db.comentarios.insert_one(document)

def find_comments(produto_id):
    return list(db.comentarios.find({"produto_id": produto_id}))
