import psycopg2
from psycopg2.extras import RealDictCursor
from database.postgres import (
    conectar, listar_categorias, listar_produtos,
    listar_fornecedores, listar_clientes, listar_lojas,
    listar_funcionarios, listar_compras, listar_itens_compra,
    fetch_vendas_por_trimestre  # ou listar_vendas se implementar
)
from database.produto_repo import (
    inserir_categoria_zodb, inserir_produto_zodb,
    inserir_fornecedor_zodb, inserir_cliente_zodb,
    inserir_loja_zodb, inserir_funcionario_zodb,
    inserir_compra_zodb, inserir_item_compra_zodb,
    inserir_estoque_zodb,
    inserir_promocao_zodb, inserir_produto_promocao_zodb,
    inserir_venda_zodb
)
from types import SimpleNamespace

def migrar_tudo_para_zodb():
    # Categorias
    for row in listar_categorias():
        inserir_categoria_zodb(row['nome_categoria'], row.get('descricao'))

    # Produtos
    for row in listar_produtos():
        p = SimpleNamespace(**row)
        p.id = row['id_produto']
        inserir_produto_zodb(p)

    # Fornecedores
    for row in listar_fornecedores():
        f = SimpleNamespace(**row)
        f.id = row['id_fornecedor']
        inserir_fornecedor_zodb(f)

    # Clientes
    for row in listar_clientes():
        c = SimpleNamespace(**row)
        c.id = row['id_cliente']
        inserir_cliente_zodb(c)

    # Lojas
    for row in listar_lojas():
        l = SimpleNamespace(**row)
        l.id_loja = row['id_loja']
        inserir_loja_zodb(l)

    # Funcionários
    for row in listar_funcionarios():
        f = SimpleNamespace(**row)
        f.id = row['id_funcionario']
        inserir_funcionario_zodb(f)

    # Compras + Itens
    for c in listar_compras():
        inserir_compra_zodb(c)
        for it in listar_itens_compra():
            if it['id_compra'] == c['id_compra']:
                inserir_item_compra_zodb(it)

    # Estoque
    # (implemente listar_estoque em postgres.py se desejar)
    # for e in listar_estoque():
    #     inserir_estoque_zodb(e)

    # Promoções & ProdutoPromocao
    # (imagine que já tenha listar_promocoes, listar_produto_promocao)
    # for prom in listar_promocoes():
    #     inserir_promocao_zodb(SimpleNamespace(**prom))
    # for pp in listar_produto_promocao():
    #     inserir_produto_promocao_zodb(pp)

    # Vendas
    vendas = fetch_vendas_por_trimestre()  # ou seu listar_vendas()
    for v in vendas:
        inserir_venda_zodb(v)
