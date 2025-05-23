# database/mongo.py
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

def conectar_mongo():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB]

def inserir_comentario(payload):
    db = conectar_mongo()
    return db.comentarios.insert_one(payload)

def listar_comentarios(produto_id):
    db = conectar_mongo()
    return list(db.comentarios.find({"produto_id": produto_id}))