from pymongo import MongoClient
from config import MONGO_URI

def conectar_mongo():
    client = MongoClient(MONGO_URI)
    return client["varejo"]
