# tests/integration_test.py

from datetime import datetime
from types import SimpleNamespace

# PostgreSQL
from database.postgres import (
    criar_tabelas,
    cadastrar_categoria, listar_categorias,
    cadastrar_produto, listar_produtos,
    cadastrar_loja, listar_lojas,
    cadastrar_funcionario, listar_funcionarios,
    cadastrar_cliente, listar_clientes,
    cadastrar_fornecedor, listar_fornecedores,
    cadastrar_compra, listar_compras,
    cadastrar_item_compra, listar_itens_compra,
    atualizar_estoque, listar_estoque,
    registrar_venda, fetch_vendas_por_trimestre
)

# MongoDB
from database.mongo import inserir_comentario, listar_comentarios

# ZODB
from database.produto_repo import (
    inserir_categoria_zodb,
    inserir_produto_zodb,
    inserir_loja_zodb,
    inserir_funcionario_zodb,
    inserir_cliente_zodb,
    inserir_fornecedor_zodb,
    inserir_compra_zodb,
    inserir_item_compra_zodb,
    inserir_estoque_zodb,
    inserir_venda_zodb,
    root,
)
from database.migrator import migrar_tudo_para_zodb

def popular_postgres():
    """Popula o Postgres com dados de teste."""
    # 1) Categorias
    cats = [
        {'nome': 'Eletrônicos', 'descricao': 'Tecnologia e informática'},
        {'nome': 'Roupas',       'descricao': 'Moda e vestuário'},
        {'nome': 'Alimentos',    'descricao': 'Comidas e bebidas'}
    ]
    for c in cats:
        cadastrar_categoria(c['nome'], c['descricao'])

    # 2) Produtos
    prods = [
        {'codigo_produto':'TST001','nome_produto':'Mouse Gamer',
         'descricao':'Mouse com DPI','id_categoria':1,'marca':'Logitech',
         'preco_atual':199.90,'unidade_medida':'UN','ativo':True},
        {'codigo_produto':'TST002','nome_produto':'Camiseta Básica',
         'descricao':'Camiseta algodão','id_categoria':2,'marca':'Hering',
         'preco_atual':49.90,'unidade_medida':'UN','ativo':True},
        {'codigo_produto':'TST003','nome_produto':'Água Mineral',
         'descricao':'Garrafa 500ml','id_categoria':3,'marca':'Crystal',
         'preco_atual':3.50,'unidade_medida':'UN','ativo':True},
    ]
    for p in prods:
        cadastrar_produto(SimpleNamespace(**p))

    # 3) Lojas
    lojas = [
        {'codigo_loja':'LT01','nome_loja':'Loja A','endereco':'Rua A,100',
         'cidade':'Recife','estado':'PE','cep':'50000-000','telefone':'81-9999',
         'gerente':'Lucas','ativa':True},
        {'codigo_loja':'LT02','nome_loja':'Loja B','endereco':'Av B,200',
         'cidade':'Olinda','estado':'PE','cep':'53000-000','telefone':'81-8888',
         'gerente':'Mariana','ativa':True},
    ]
    for l in lojas:
        cadastrar_loja(SimpleNamespace(**l))

    # 4) Funcionários
    funcs = [
        {'codigo_funcionario':'TF01','nome':'João','cargo':'Vendedor','id_loja':1,'salario':2000.00,'ativo':True},
        {'codigo_funcionario':'TF02','nome':'Ana','cargo':'Caixa','id_loja':2,'salario':1800.00,'ativo':True},
    ]
    for f in funcs:
        cadastrar_funcionario(SimpleNamespace(**f))

    # 5) Clientes
    cli = {'cpf':'12345678901','nome':'Cliente A','email':'a@test.com',
           'telefone':'81-7777','endereco':'Rua C,300','cidade':'Recife',
           'estado':'PE','cep':'50000-111','ativo':True}
    cadastrar_cliente(SimpleNamespace(**cli))

    # 6) Fornecedores
    forn = {'cnpj':'12345678000199','razao_social':'FornX','nome_fantasia':'Fornecedor X',
            'telefone':'81-6666','email':'x@forn.com','endereco':'Av D,400',
            'cidade':'Recife','estado':'PE','ativo':True}
    cadastrar_fornecedor(SimpleNamespace(**forn))

    # 7) Compras e itens de compra
    cp = {'numero_compra':'CP01','id_fornecedor':1,'id_loja':1,
          'data_compra':'2025-05-01 10:00:00','valor_total':500.00,'status_compra':'confirmada'}
    comprar_id = cadastrar_compra(cp)
    ic = {'id_compra':comprar_id,'id_produto':1,'quantidade':2,'preco_unitario':199.90}
    cadastrar_item_compra(ic)

    # 8) Estoque
    est = {'id_produto':1,'id_loja':1,'quantidade_atual':5,'quantidade_minima':2,'quantidade_maxima':10}
    atualizar_estoque(est)

    # 9) Vendas
    registrar_venda(1, 1, 199.90, datetime.strptime('2025-05-02','%Y-%m-%d'))

    #10) Comentários (Mongo)
    inserir_comentario({
        'produto_id':1,'cliente':'Cliente A','comentario':'Ótimo!','data':datetime.now().isoformat(),'imagens':[]
    })
    print("▶ Postgres e MongoDB populados.")

def resumo_counts():
    """Imprime contagens em cada camada."""
    print("\n--- Postgres: contagens ---")
    print("categorias:",    len(listar_categorias()))
    print("produtos:",      len(listar_produtos()))
    print("lojas:",         len(listar_lojas()))
    print("funcionarios:",  len(listar_funcionarios()))
    print("clientes:",      len(listar_clientes()))
    print("fornecedores:",  len(listar_fornecedores()))
    print("compras:",       len(listar_compras()))
    print("item_compra:",   len(listar_itens_compra()))
    print("estoque:",       len(listar_estoque()))
    print("vendas(tri):",   len(fetch_vendas_por_trimestre()))
    # comentários via listar_comentarios(pid)
    print("comentários p/ produto 1:", len(listar_comentarios(1)))

    print("\n--- ZODB: contagens ---")
    for name, tree in root.items():
        # ignore next_ids
        if name == 'next_ids': continue
        print(f"{name:20s}", getattr(tree, 'len', None) or len(tree))

def test_integracao():
    print("=== INICIANDO TESTE DE INTEGRAÇÃO MULTIMODELO ===")
    criar_tabelas()
    popular_postgres()
    resumo_counts()

    # replicar tudo de Postgres → ZODB
    print("\n▶ Migrando Postgres → ZODB...")
    migrar_tudo_para_zodb()
    resumo_counts()
    print("=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_integracao()
