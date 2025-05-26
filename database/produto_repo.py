from ZODB import DB, FileStorage
from persistent import Persistent
from BTrees.OOBTree import OOBTree
import transaction

# Modelo de domínio para Produto
class Produto:
    def __init__(
        self,
        codigo_produto: str,
        nome_produto: str,
        descricao: str,
        id_categoria: int,
        marca: str,
        preco_atual: float,
        unidade_medida: str,
        ativo: bool = True
    ):
        self.id = None
        self.codigo_produto = codigo_produto
        self.nome_produto = nome_produto
        self.descricao = descricao
        self.id_categoria = id_categoria
        self.marca = marca
        self.preco_atual = preco_atual
        self.unidade_medida = unidade_medida
        self.ativo = ativo

    def __repr__(self):
        status = 'Sim' if self.ativo else 'Não'
        return (
            f"[{self.id}] {self.codigo_produto} - {self.nome_produto} ({self.marca}) - "
            f"R${self.preco_atual:.2f} [{self.unidade_medida}] | Ativo: {status}"
        )

# Inicializa/abre o banco ZODB
storage = FileStorage.FileStorage('zodb_storage.fs')
db = DB(storage)
conn = db.open()
root = conn.root()

# Prepara a árvore de produtos e o contador de IDs
if 'produtos' not in root:
    root['produtos'] = OOBTree()
    root['next_produto_id'] = 1
    transaction.commit()

# Classe persistente baseada no modelo Produto
class PersistentProduto(Produto, Persistent):
    pass

# --- Repositório ZODB para Produtos ---

def inserir_produto(produto: Produto) -> int:
    """
    Persiste um Produto no ZODB e retorna seu ID.
    """
    # Cria uma cópia persistente
    p = PersistentProduto(
        produto.codigo_produto,
        produto.nome_produto,
        produto.descricao,
        produto.id_categoria,
        produto.marca,
        produto.preco_atual,
        produto.unidade_medida,
        produto.ativo
    )
    pid = root['next_produto_id']
    p.id = pid
    root['produtos'][pid] = p
    root['next_produto_id'] = pid + 1
    transaction.commit()
    return pid


def fetch_todos_os_produtos() -> list[Produto]:
    """
    Retorna a lista de todos os Produtos armazenados no ZODB.
    """
    return list(root['produtos'].values())


def buscar_produto(produto_id: int) -> Produto | None:
    """
    Retorna o Produto com o ID informado, ou None se não existir.
    """
    return root['produtos'].get(produto_id)


def fechar_banco():
    """
    Fecha a conexão com o banco ZODB.
    """
    conn.close()
    db.close()