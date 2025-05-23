from database import postgres, mongo
from modelos.produto import Produto

# Conectar e criar tabelas
postgres.criar_tabelas()

# Criar produto no estilo ObjectDB
produto = Produto("Tênis", "Calçados", "Nike", 299.90, 20)
print("Produto criado:", produto)

# Inserir comentário no MongoDB
db_mongo = mongo.conectar_mongo()
comentarios = db_mongo["comentarios"]

comentarios.insert_one({
    "produto_id": 1,
    "comentarios": [
        { "cliente": "Ana", "comentario": "Muito bom!", "data": "2025-05-19" }
    ],
    "imagens": ["https://img.com/tenis1.jpg"]
})

print("Comentário inserido no MongoDB.")
