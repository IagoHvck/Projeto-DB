from ZODB import DB
from ZODB.FileStorage import FileStorage
from persistent import Persistent
from persistent.list import PersistentList
from BTrees.OOBTree import OOBTree
import transaction

# —————— Classes de Domínio (para CRUD e ZODB) ——————
# Definições originais necessárias em main.py
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

class Cliente:
    def __init__(self, cpf, nome, email, telefone, endereco, cidade, estado, cep, ativo=True):
        self.cpf = cpf
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        self.ativo = ativo

class Loja:
    def __init__(self, codigo_loja, nome_loja, endereco, cidade, estado, cep, telefone, gerente, ativa=True):
        self.codigo_loja = codigo_loja
        self.nome_loja = nome_loja
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        self.telefone = telefone
        self.gerente = gerente
        self.ativa = ativa

# —————— Classes de Domínio ZODB ——————
class ZCategoria(Persistent):
    def __init__(self, id_categoria, nome_categoria, descricao=None):
        self.id_categoria = id_categoria
        self.nome_categoria = nome_categoria
        self.descricao = descricao
        self.produtos = PersistentList()

class ZProduto(Persistent):
    def __init__(self, id_produto, codigo_produto, nome_produto, descricao,
                 preco_atual, categoria, marca=None, unidade_medida=None, ativo=True):
        self.id_produto = id_produto
        self.codigo_produto = codigo_produto
        self.nome_produto = nome_produto
        self.descricao = descricao
        self.preco_atual = preco_atual
        self.categoria = categoria
        self.marca = marca
        self.unidade_medida = unidade_medida
        self.ativo = ativo
        self.fornecedores = PersistentList()
        categoria.produtos.append(self)

class ZFornecedor(Persistent):
    def __init__(self, cnpj, razao_social, nome_fantasia,
                 telefone=None, email=None, endereco=None,
                 cidade=None, estado=None, ativo=True):
        self.cnpj = cnpj
        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.telefone = telefone
        self.email = email
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.ativo = ativo
        self.produtos = PersistentList()

class ZProdutoFornecedor(Persistent):
    def __init__(self, produto, fornecedor, preco_compra, prazo_entrega):
        self.produto = produto
        self.fornecedor = fornecedor
        self.preco_compra = preco_compra
        self.prazo_entrega = prazo_entrega
        produto.fornecedores.append(self)
        fornecedor.produtos.append(self)

class ZEstoque(Persistent):
    def __init__(self, produto, loja, quantidade_atual,
                 quantidade_minima, quantidade_maxima):
        self.produto = produto
        self.loja = loja
        self.quantidade_atual = quantidade_atual
        self.quantidade_minima = quantidade_minima
        self.quantidade_maxima = quantidade_maxima

class ZPromocao(Persistent):
    def __init__(self, id_promocao, nome_promocao, descricao,
                 data_inicio, data_fim, percentual_desconto, ativa=True):
        self.id_promocao = id_promocao
        self.nome_promocao = nome_promocao
        self.descricao = descricao
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.percentual_desconto = percentual_desconto
        self.ativa = ativa
        self.produtos = PersistentList()

class ZProdutoPromocao(Persistent):
    def __init__(self, produto, promocao, preco_promocional):
        self.produto = produto
        self.promocao = promocao
        self.preco_promocional = preco_promocional
        promocao.produtos.append(self)

# —————— ZODB Setup ——————
storage = FileStorage('zodb_storage.fs')
db = DB(storage)
conn = db.open()
root = conn.root()

# Inicializa coleções
collections = ['categorias','produtos','fornecedores','produto_fornecedores',
               'estoques','promocoes','produto_promocoes']
for col in collections:
    if col not in root:
        root[col] = OOBTree()
# Contadores
if 'next_ids' not in root:
    root['next_ids'] = {k:1 for k in ['categoria','produto','fornecedor','pf','estoque','promocao','pp']}
transaction.commit()

# —————— Inserções ZODB ——————
def inserir_categoria_zodb(nome_categoria, descricao=None):
    nid = root['next_ids']['categoria']
    z = ZCategoria(nid, nome_categoria, descricao)
    root['categorias'][nid] = z
    root['next_ids']['categoria'] += 1
    transaction.commit()
    return nid

def inserir_produto_zodb(prod):
    pid = root['next_ids']['produto']
    cat = root['categorias'][prod.id_categoria]
    z = ZProduto(pid, prod.codigo_produto, prod.nome_produto,
                 prod.descricao, prod.preco_atual, cat,
                 prod.marca, prod.unidade_medida, prod.ativo)
    root['produtos'][pid] = z
    root['next_ids']['produto'] += 1
    transaction.commit()
    return pid

def inserir_fornecedor_zodb(f):
    fid = root['next_ids']['fornecedor']
    z = ZFornecedor(f.cnpj, f.razao_social, f.nome_fantasia,
                    f.telefone, f.email, f.endereco,
                    f.cidade, f.estado, f.ativo)
    root['fornecedores'][fid] = z
    root['next_ids']['fornecedor'] += 1
    transaction.commit()
    return fid

def inserir_produto_fornecedor_zodb(rel):
    pfid = root['next_ids']['pf']
    p = root['produtos'][rel.produto.id]
    f = root['fornecedores'][rel.fornecedor.id]
    z = ZProdutoFornecedor(p, f, rel.preco_compra, rel.prazo_entrega)
    root['produto_fornecedores'][pfid] = z
    root['next_ids']['pf'] += 1
    transaction.commit()
    return pfid

def inserir_estoque_zodb(est):
    eid = root['next_ids']['estoque']
    p = root['produtos'][est.produto.id]
    # loja deve ter repositório semelhante a produtos
    z = ZEstoque(p, est.loja, est.quantidade_atual,
                 est.quantidade_minima, est.quantidade_maxima)
    root['estoques'][eid] = z
    root['next_ids']['estoque'] += 1
    transaction.commit()
    return eid

def inserir_promocao_zodb(prom):
    prid = root['next_ids']['promocao']
    z = ZPromocao(prid, prom.nome_promocao, prom.descricao,
                  prom.data_inicio, prom.data_fim,
                  prom.percentual_desconto, prom.ativa)
    root['promocoes'][prid] = z
    root['next_ids']['promocao'] += 1
    transaction.commit()
    return prid

def inserir_produto_promocao_zodb(rel):
    ppid = root['next_ids']['pp']
    p = root['produtos'][rel.produto.id]
    prom = root['promocoes'][rel.promocao.id_promocao]
    z = ZProdutoPromocao(p, prom, rel.preco_promocional)
    root['produto_promocoes'][ppid] = z
    root['next_ids']['pp'] += 1
    transaction.commit()
    return ppid

# —————— Replicação Postgres -> ZODB ——————
def replicar_para_zodb():
    from database.postgres import (
        listar_categorias, listar_produtos, listar_fornecedores,
        # caso itens e promoções estiverem em Postgres, importe também
    )
    for c in listar_categorias():
        inserir_categoria_zodb(c['nome_categoria'], c.get('descricao'))
    for p in listar_produtos():
        inserir_produto_zodb(p)
    for f in listar_fornecedores():
        inserir_fornecedor_zodb(f)
    transaction.commit()

# —————— Fechamento ——————
def fechar_banco():
    conn.close()
    db.close()
