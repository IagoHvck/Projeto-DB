# database/produto_repo.py
from ZODB import DB, FileStorage
from persistent import Persistent
from BTrees.OOBTree import OOBTree
import transaction

# —————— Classes de Domínio ——————

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
            f"[{self.id}] {self.codigo_produto} - {self.nome_produto} "
            f"({self.marca}) R${self.preco_atual:.2f} [{self.unidade_medida}] | Ativo: {status}"
        )

class Cliente:
    def __init__(self, cpf, nome, email, telefone, endereco, cidade, estado, cep, ativo=True):
        self.cpf       = cpf
        self.nome      = nome
        self.email     = email
        self.telefone  = telefone
        self.endereco  = endereco
        self.cidade    = cidade
        self.estado    = estado
        self.cep       = cep
        self.ativo     = ativo

class Loja:
    def __init__(self, codigo_loja, nome_loja, endereco, cidade, estado, cep, telefone, gerente, ativa=True):
        self.codigo_loja = codigo_loja
        self.nome_loja   = nome_loja
        self.endereco    = endereco
        self.cidade      = cidade
        self.estado      = estado
        self.cep         = cep
        self.telefone    = telefone
        self.gerente     = gerente
        self.ativa       = ativa

# —————— ZODB para Produto ——————

# Inicializa/abre o banco ZODB
storage = FileStorage.FileStorage('zodb_storage.fs')
db      = DB(storage)
conn    = db.open()
root    = conn.root()

if 'produtos' not in root:
    root['produtos'] = OOBTree()
    root['next_produto_id'] = 1
    transaction.commit()

class PersistentProduto(Produto, Persistent):
    pass

def inserir_produto(produto: Produto) -> int:
    """
    Persiste um Produto no ZODB e retorna seu ID.
    """
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
    return list(root['produtos'].values())

def buscar_produto(produto_id: int) -> Produto | None:
    return root['produtos'].get(produto_id)

def fechar_banco():
    conn.close()
    db.close()
