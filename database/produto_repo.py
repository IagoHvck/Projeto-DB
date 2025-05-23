# database/produto_repo.py
from ZODB import DB, FileStorage
from persistent import Persistent
from BTrees.OOBTree import OOBTree
import transaction
from modelos.produto import Produto as ProdutoModel

# Inicializa/abre o banco ZODB
storage = FileStorage.FileStorage('zodb_storage.fs')
db      = DB(storage)
conn    = db.open()
root    = conn.root()

# prepara a árvore
if 'produtos' not in root:
    root['produtos'] = OOBTree()
    root['next_produto_id'] = 1
    transaction.commit()

# define já no módulo a classe persistente
class PersistentProduto(ProdutoModel, Persistent):
    pass

def inserir_produto(produto: ProdutoModel) -> int:
    """
    Persiste um Produto no ZODB e retorna seu ID.
    """
    # cria um novo PersistentProduto copiando os dados
    p = PersistentProduto(
        produto.nome,
        produto.categoria,
        produto.marca,
        produto.preco,
        produto.estoque
    )
    pid = root['next_produto_id']
    p.id = pid
    root['produtos'][pid] = p
    root['next_produto_id'] = pid + 1
    transaction.commit()
    return pid

def fetch_todos_os_produtos() -> list:
    return list(root['produtos'].values())

def buscar_produto(produto_id: int) -> ProdutoModel:
    return root['produtos'].get(produto_id, None)

def fechar_banco():
    conn.close()
    db.close()
