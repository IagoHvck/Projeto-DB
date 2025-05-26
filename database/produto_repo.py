# database/produto_repo.py

from ZODB import DB
from ZODB.FileStorage import FileStorage
from persistent import Persistent
from persistent.list import PersistentList
from BTrees.OOBTree import OOBTree
import transaction

# ——— Modelos de Domínio (usados também no main.py) ———

class Produto:
    def __init__(self, codigo_produto, nome_produto, descricao,
                 id_categoria, marca, preco_atual, unidade_medida, ativo=True):
        self.id = None
        self.codigo_produto = codigo_produto
        self.nome_produto   = nome_produto
        self.descricao      = descricao
        self.id_categoria   = id_categoria
        self.marca          = marca
        self.preco_atual    = preco_atual
        self.unidade_medida = unidade_medida
        self.ativo          = ativo
    def __repr__(self):
        st = "Ativo" if self.ativo else "Inativo"
        return (f"[{self.id}] {self.codigo_produto} • {self.nome_produto} "
                f"({self.marca}) R${self.preco_atual:.2f} • {st}")

class Cliente:
    def __init__(self, cpf, nome, email, telefone, endereco, cidade, estado, cep, ativo=True):
        self.id = None
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
        self.id_loja    = None
        self.codigo_loja= codigo_loja
        self.nome_loja  = nome_loja
        self.endereco   = endereco
        self.cidade     = cidade
        self.estado     = estado
        self.cep        = cep
        self.telefone   = telefone
        self.gerente    = gerente
        self.ativa      = ativa

class Funcionario:
    def __init__(self, codigo_funcionario, nome, cargo, id_loja, salario, ativo=True):
        self.id = None
        self.codigo_funcionario = codigo_funcionario
        self.nome      = nome
        self.cargo     = cargo
        self.id_loja   = id_loja
        self.salario   = salario
        self.ativo     = ativo

# ——— ZODB Setup ———

storage = FileStorage('zodb_storage.fs')
db      = DB(storage)
conn    = db.open()
root    = conn.root()

# Cria todas as “tabelas” (OOBTree) e contadores
names = [
  'categorias','produtos','fornecedores','produto_fornecedores',
  'estoques','promocoes','produto_promocoes',
  'clientes','lojas','funcionarios',
  'compras','item_compras','vendas'
]
for n in names:
    if n not in root:
        root[n] = OOBTree()
if 'next_ids' not in root:
    root['next_ids'] = {}
for k in [
    'categoria','produto','fornecedor','pf','estoque','promocao','pp',
    'cliente','loja','funcionario','compra','item_compra','venda'
]:
    root['next_ids'].setdefault(k, 1)
transaction.commit()

# ——— Classes Persistentes ZODB ———

class ZCategoria(Persistent):
    def __init__(self, id, nome, descricao=None):
        self.id_categoria = id
        self.nome_categoria = nome
        self.descricao = descricao
        self.produtos  = PersistentList()

class ZProduto(Persistent):
    def __init__(self, id_produto, codigo, nome, descricao, preco, categoria, marca, unidade, ativo):
        self.id_produto    = id_produto
        self.codigo_produto= codigo
        self.nome_produto  = nome
        self.descricao     = descricao
        self.preco_atual   = preco
        self.categoria     = categoria
        self.marca         = marca
        self.unidade_medida= unidade
        self.ativo         = ativo
        self.fornecedores  = PersistentList()
        if categoria is not None:
            categoria.produtos.append(self)

class ZFornecedor(Persistent):
    def __init__(self, f):  # f: SimpleNamespace ou similar
        self.id_fornecedor = None
        self.cnpj          = f.cnpj
        self.razao_social  = f.razao_social
        self.nome_fantasia = f.nome_fantasia
        self.telefone      = f.telefone
        self.email         = f.email
        self.endereco      = f.endereco
        self.cidade        = f.cidade
        self.estado        = f.estado
        self.ativo         = f.ativo
        self.produtos      = PersistentList()

class ZProdutoFornecedor(Persistent):
    def __init__(self, zprod:ZProduto, zforn:ZFornecedor, preco_compra, prazo_entrega):
        self.produto       = zprod
        self.fornecedor    = zforn
        self.preco_compra  = preco_compra
        self.prazo_entrega = prazo_entrega
        zprod.fornecedores.append(self)
        zforn.produtos.append(self)

class ZEstoque(Persistent):
    def __init__(self, zprod:ZProduto, zloja:Loja, qa, qmin, qmax):
        self.produto          = zprod
        self.loja             = zloja
        self.quantidade_atual = qa
        self.quantidade_minima= qmin
        self.quantidade_maxima= qmax

class ZPromocao(Persistent):
    def __init__(self, id, prom):
        self.id_promocao        = id
        self.nome_promocao      = prom.nome_promocao
        self.descricao          = prom.descricao
        self.data_inicio        = prom.data_inicio
        self.data_fim           = prom.data_fim
        self.percentual_desconto= prom.percentual_desconto
        self.ativa              = prom.ativa
        self.produtos           = PersistentList()

class ZProdutoPromocao(Persistent):
    def __init__(self, zprod:ZProduto, zprom:ZPromocao, preco_promocional):
        self.produto           = zprod
        self.promocao          = zprom
        self.preco_promocional = preco_promocional
        zprom.produtos.append(self)

class ZCliente(Persistent):
    def __init__(self, id_cliente, cpf, nome, email, telefone, endereco, cidade, estado, cep, ativo):
        self.id_cliente = id_cliente
        self.cpf        = cpf
        self.nome       = nome
        self.email      = email
        self.telefone   = telefone
        self.endereco   = endereco
        self.cidade     = cidade
        self.estado     = estado
        self.cep        = cep
        self.ativo      = ativo

class ZLoja(Persistent):
    def __init__(self, id_loja, codigo, nome, endereco, cidade, estado, cep, telefone, gerente, ativa):
        self.id_loja      = id_loja
        self.codigo_loja  = codigo
        self.nome_loja    = nome
        self.endereco     = endereco
        self.cidade       = cidade
        self.estado       = estado
        self.cep          = cep
        self.telefone     = telefone
        self.gerente      = gerente
        self.ativa        = ativa

class ZFuncionario(Persistent):
    def __init__(self, id_funcionario, codigo, nome, cargo, zloja, salario, ativo):
        self.id_funcionario     = id_funcionario
        self.codigo_funcionario = codigo
        self.nome               = nome
        self.cargo              = cargo
        self.loja               = zloja
        self.salario            = salario
        self.ativo              = ativo

class ZCompra(Persistent):
    def __init__(self, id_compra, numero, zforn, zloja, data_compra, valor_total, status_compra):
        self.id_compra    = id_compra
        self.numero_compra= numero
        self.fornecedor   = zforn
        self.loja         = zloja
        self.data_compra  = data_compra
        self.valor_total  = valor_total
        self.status_compra= status_compra
        self.itens        = PersistentList()

class ZItemCompra(Persistent):
    def __init__(self, id_item, zcompra, zprod, quantidade, preco_unitario, valor_total):
        self.id_item       = id_item
        self.compra        = zcompra
        self.produto       = zprod
        self.quantidade    = quantidade
        self.preco_unitario= preco_unitario
        self.valor_total   = valor_total

class ZVenda(Persistent):
    def __init__(self, id_venda, zprod, quantidade, valor_total, data_venda):
        self.id_venda    = id_venda
        self.produto     = zprod
        self.quantidade  = quantidade
        self.valor_total = valor_total
        self.data_venda  = data_venda

# ——— Funções de Inserção ZODB ———

def inserir_categoria_zodb(nome, descricao=None):
    nid = root['next_ids']['categoria']
    z = ZCategoria(nid, nome, descricao)
    root['categorias'][nid] = z
    root['next_ids']['categoria'] += 1
    transaction.commit()
    return nid

def inserir_produto_zodb(prod: Produto) -> int:
    pid = root['next_ids']['produto']
    zcat = root['categorias'].get(prod.id_categoria)
    z = ZProduto(
        pid,
        prod.codigo_produto, prod.nome_produto, prod.descricao,
        prod.preco_atual, zcat, prod.marca, prod.unidade_medida, prod.ativo
    )
    root['produtos'][pid] = z
    root['next_ids']['produto'] += 1
    transaction.commit()
    return pid

def inserir_fornecedor_zodb(f) -> int:
    fid = root['next_ids']['fornecedor']
    z = ZFornecedor(f)
    z.id_fornecedor = fid
    root['fornecedores'][fid] = z
    root['next_ids']['fornecedor'] += 1
    transaction.commit()
    return fid

def inserir_produto_fornecedor_zodb(rel) -> int:
    pfid = root['next_ids']['pf']
    zp = root['produtos'][rel.produto.id]
    zf = root['fornecedores'][rel.fornecedor.id]
    z = ZProdutoFornecedor(zp, zf, rel.preco_compra, rel.prazo_entrega)
    root['produto_fornecedores'][pfid] = z
    root['next_ids']['pf'] += 1
    transaction.commit()
    return pfid

def inserir_estoque_zodb(est) -> int:
    eid = root['next_ids']['estoque']
    zp = root['produtos'][est.produto.id]
    z = ZEstoque(zp, est.loja, est.quantidade_atual, est.quantidade_minima, est.quantidade_maxima)
    root['estoques'][eid] = z
    root['next_ids']['estoque'] += 1
    transaction.commit()
    return eid

def inserir_promocao_zodb(prom) -> int:
    prid = root['next_ids']['promocao']
    z = ZPromocao(prid, prom)
    root['promocoes'][prid] = z
    root['next_ids']['promocao'] += 1
    transaction.commit()
    return prid

def inserir_produto_promocao_zodb(rel) -> int:
    ppid = root['next_ids']['pp']
    zp   = root['produtos'][rel.produto.id]
    zpmo = root['promocoes'][rel.promocao.id_promocao]
    z = ZProdutoPromocao(zp, zpmo, rel.preco_promocional)
    root['produto_promocoes'][ppid] = z
    root['next_ids']['pp'] += 1
    transaction.commit()
    return ppid

def inserir_cliente_zodb(c) -> int:
    nid = root['next_ids']['cliente']
    z = ZCliente(nid, c.cpf, c.nome, c.email, c.telefone,
                 c.endereco, c.cidade, c.estado, c.cep, c.ativo)
    root['clientes'][nid] = z
    root['next_ids']['cliente'] += 1
    transaction.commit()
    return nid

def inserir_loja_zodb(l) -> int:
    nid = root['next_ids']['loja']
    z = ZLoja(nid, l.codigo_loja, l.nome_loja, l.endereco,
              l.cidade, l.estado, l.cep, l.telefone, l.gerente, l.ativa)
    root['lojas'][nid] = z
    root['next_ids']['loja'] += 1
    transaction.commit()
    return nid

def inserir_funcionario_zodb(f) -> int:
    nid = root['next_ids']['funcionario']
    zloja = root['lojas'][f.id_loja]
    z = ZFuncionario(nid, f.codigo_funcionario, f.nome, f.cargo,
                     zloja, f.salario, f.ativo)
    root['funcionarios'][nid] = z
    root['next_ids']['funcionario'] += 1
    transaction.commit()
    return nid

def inserir_compra_zodb(c: dict) -> int:
    nid = root['next_ids']['compra']
    zforn = root['fornecedores'][c['id_fornecedor']]
    zloja = root['lojas'][c['id_loja']]
    z = ZCompra(nid, c['numero_compra'], zforn, zloja,
                c['data_compra'], c['valor_total'], c['status_compra'])
    root['compras'][nid] = z
    root['next_ids']['compra'] += 1
    transaction.commit()
    return nid

def inserir_item_compra_zodb(i: dict) -> int:
    nid   = root['next_ids']['item_compra']
    zcomp = root['compras'][i['id_compra']]
    zprod = root['produtos'][i['id_produto']]
    valor = i.get('valor_total', i['quantidade'] * i['preco_unitario'])
    z = ZItemCompra(nid, zcomp, zprod, i['quantidade'], i['preco_unitario'], valor)
    zcomp.itens.append(z)
    root['item_compras'][nid] = z
    root['next_ids']['item_compra'] += 1
    transaction.commit()
    return nid

def inserir_venda_zodb(v: dict) -> int:
    nid   = root['next_ids']['venda']
    zprod = root['produtos'][v['id_produto']]
    z = ZVenda(nid, zprod, v['quantidade'], v['valor_total'], v['data_venda'])
    root['vendas'][nid] = z
    root['next_ids']['venda'] += 1
    transaction.commit()
    return nid

def fechar_banco():
    conn.close()
    db.close()

# ——— Alias para chamar do main.py ———
# replicar tudo de Postgres → ZODB
from database.migrator import migrar_tudo_para_zodb as replicar_para_zodb
