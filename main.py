# main.py
from datetime import datetime
from database.postgres import (
    criar_tabelas,
    # -- CRUD Categoria
    cadastrar_categoria, listar_categorias,
    # -- CRUD Produto
    cadastrar_produto, listar_produtos,
    # -- CRUD Cliente
    cadastrar_cliente, listar_clientes,
    # -- CRUD Loja
    cadastrar_loja, listar_lojas,
    # -- CRUD Funcionário
    cadastrar_funcionario, listar_funcionarios,
    # -- CRUD Fornecedor
    cadastrar_fornecedor, listar_fornecedores,
    # -- CRUD Compra e ItemCompra
    cadastrar_compra, listar_compras,
    cadastrar_item_compra,
    # -- CRUD Venda e ItemVenda
    registrar_venda, listar_vendas_por_trimestre,
    cadastrar_item_venda,
    # -- CRUD Estoque
    cadastrar_estoque, listar_estoques,
    # -- CRUD Promoção e ProdutoPromocao
    cadastrar_promocao, listar_promocoes,
    cadastrar_produto_promocao, listar_produtos_promocao,
)
from database.produto_repo import inserir_produto as inserir_produto_zodb, fetch_todos_os_produtos
from database.mongo import inserir_comentario, listar_comentarios
from utils.analises import exibir_vendas_por_trimestre, exibir_comentarios

def menu():
    print("""
======== MENU ========
1) Criar/Atualizar esquemas
2) CRUD Categoria
3) CRUD Produto
4) CRUD Cliente
5) CRUD Loja
6) CRUD Funcionário
7) CRUD Fornecedor
8) CRUD Compra/Itens
9) CRUD Venda/Itens
10) CRUD Estoque
11) CRUD Promoções
12) NoSQL Comentários
0) Sair
""")

def submenu_crud(nome, acoes):
    print(f"\n-- {nome} --")
    for k, v in acoes.items():
        print(f"{k}) {v[0]}")
    print("0) Voltar")
    return input("> ").strip()

def main():
    while True:
        menu(); opt = input("> ").strip()
        if opt == "1":
            criar_tabelas()
            print("✅ Esquemas criados/atualizados.\n")

        elif opt == "2":
            # Categoria
            a = {
                "1": ("Listar categorias", lambda: print(*listar_categorias(), sep="\n")),
                "2": ("Criar categoria", lambda: criar_categoria_flow()),
            }
            sub = submenu_crud("Categoria", a)
            if sub in a: a[sub][1]()

        elif opt == "3":
            # Produto
            a = {
                "1": ("Listar produtos (SQL)", lambda: print(*listar_produtos(), sep="\n")),
                "2": ("Cadastrar produto", lambda: criar_produto_flow()),
                "3": ("Listar produtos (ZODB)", lambda: print(*fetch_todos_os_produtos(), sep="\n")),
            }
            sub = submenu_crud("Produto", a)
            if sub in a: a[sub][1]()

        elif opt == "4":
            # Cliente
            a = {
                "1": ("Listar clientes", lambda: print(*listar_clientes(), sep="\n")),
                "2": ("Cadastrar cliente", lambda: criar_cliente_flow()),
            }
            sub = submenu_crud("Cliente", a)
            if sub in a: a[sub][1]()

        elif opt == "5":
            # Loja
            a = {
                "1": ("Listar lojas", lambda: print(*listar_lojas(), sep="\n")),
                "2": ("Cadastrar loja", lambda: criar_loja_flow()),
            }
            sub = submenu_crud("Loja", a)
            if sub in a: a[sub][1]()

        elif opt == "6":
            # Funcionário
            a = {
                "1": ("Listar funcionários", lambda: print(*listar_funcionarios(), sep="\n")),
                "2": ("Cadastrar funcionário", lambda: criar_funcionario_flow()),
            }
            sub = submenu_crud("Funcionário", a)
            if sub in a: a[sub][1]()

        elif opt == "7":
            # Fornecedor
            a = {
                "1": ("Listar fornecedores", lambda: print(*listar_fornecedores(), sep="\n")),
                "2": ("Cadastrar fornecedor", lambda: criar_fornecedor_flow()),
            }
            sub = submenu_crud("Fornecedor", a)
            if sub in a: a[sub][1]()

        elif opt == "8":
            # Compra e Itens
            a = {
                "1": ("Listar compras", lambda: print(*listar_compras(), sep="\n")),
                "2": ("Cadastrar compra", lambda: criar_compra_flow()),
                "3": ("Cadastrar item de compra", lambda: criar_item_compra_flow()),
            }
            sub = submenu_crud("Compra/ItemCompra", a)
            if sub in a: a[sub][1]()

        elif opt == "9":
            # Venda e Itens
            a = {
                "1": ("Vendas por trimestre", lambda: exibir_vendas_por_trimestre(listar_vendas_por_trimestre())),
                "2": ("Registrar venda", lambda: criar_venda_flow()),
                "3": ("Cadastrar item de venda", lambda: criar_item_venda_flow()),
            }
            sub = submenu_crud("Venda/ItemVenda", a)
            if sub in a: a[sub][1]()

        elif opt == "10":
            # Estoque
            a = {
                "1": ("Listar estoques", lambda: print(*listar_estoques(), sep="\n")),
                "2": ("Cadastrar estoque", lambda: criar_estoque_flow()),
            }
            sub = submenu_crud("Estoque", a)
            if sub in a: a[sub][1]()

        elif opt == "11":
            # Promoções
            a = {
                "1": ("Listar promoções", lambda: print(*listar_promocoes(), sep="\n")),
                "2": ("Cadastrar promoção", lambda: criar_promocao_flow()),
                "3": ("Cadastrar produto em promoção", lambda: criar_produto_promocao_flow()),
            }
            sub = submenu_crud("Promoções", a)
            if sub in a: a[sub][1]()

        elif opt == "12":
            # NoSQL Comentários
            print("1) Inserir comentário")
            print("2) Listar comentários por produto")
            sub = input("> ").strip()
            if sub == "1":
                pid = int(input("ID do produto: "))
                cli = input("Cliente: ")
                com = input("Comentário: ")
                data = datetime.now().isoformat()
                imgs = input("URLs separadas por vírgula: ").split(",")
                inserir_comentario({
                    "produto_id": pid,
                    "cliente": cli,
                    "comentario": com,
                    "data": data,
                    "imagens": [u.strip() for u in imgs if u.strip()]
                })
                print("✅ Comentário inserido.")
            elif sub == "2":
                pid = int(input("ID do produto: "))
                exibir_comentarios(listar_comentarios(pid))
            else:
                print("Opção inválida.")

        elif opt == "0":
            print("Até mais!")
            break

        else:
            print("Opção inválida.\n")

# —————————————— Flows auxiliares ——————————————
def criar_categoria_flow():
    n = input("Nome: ")
    d = input("Descrição: ")
    print("ID =", cadastrar_categoria(n, d))

def criar_produto_flow():
    cats = listar_categorias()
    print("Categorias:", *[f"{c['id_categoria']}:{c['nome_categoria']}" for c in cats])
    p = Produto(
        codigo_produto = input("Código: "),
        nome_produto   = input("Nome: "),
        descricao      = input("Descrição: "),
        id_categoria   = int(input("ID da categoria: ")),
        marca          = input("Marca: "),
        preco_atual    = float(input("Preço: ")),
        unidade_medida = input("Unidade: "),
        ativo          = (input("Ativo? (s/N): ").lower()=="s")
    )
    sid = cadastrar_produto(p)
    zid = inserir_produto_zodb(p)
    print(f"SQL ID={sid}, ZODB ID={zid}")

def criar_cliente_flow():
    print("Valores: cpf, nome, email, telefone, endereco, cidade, estado, cep")
    args = [input(f"{f}: ") for f in ("cpf","nome","email","telefone","endereco","cidade","estado","cep")]
    print("ID =", cadastrar_cliente(*args))

def criar_loja_flow():
    print("Valores: codigo_loja,nome_loja,endereco,cidade,estado,cep,telefone,gerente")
    args = [input(f"{f}: ") for f in ("codigo_loja","nome_loja","endereco","cidade","estado","cep","telefone","gerente")]
    print("ID =", cadastrar_loja(*args))

def criar_funcionario_flow():
    print("Valores: codigo_funcionario,nome,cargo,id_loja,salario")
    args = [
        input("Código: "),
        input("Nome: "),
        input("Cargo: "),
        int(input("ID da loja: ")),
        float(input("Salário: "))
    ]
    print("ID =", cadastrar_funcionario(*args))

def criar_fornecedor_flow():
    print("Valores: cnpj,razao_social,nome_fantasia,telefone,email,endereco,cidade,estado")
    args = [input(f"{f}: ") for f in ("cnpj","razao_social","nome_fantasia","telefone","email","endereco","cidade","estado")]
    print("ID =", cadastrar_fornecedor(*args))

def criar_compra_flow():
    print("Valores: numero_compra,id_fornecedor,id_loja,data_compra,valor_total,status")
    args = [
        input("Número: "),
        int(input("ID fornecedor: ")),
        int(input("ID loja: ")),
        datetime.strptime(input("Data (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M"),
        float(input("Valor total: ")),
        input("Status: ")
    ]
    print("ID =", cadastrar_compra(*args))

def criar_item_compra_flow():
    print("Valores: id_compra,id_produto,quantidade,preco_unitario,valor_total")
    args = [
        int(input("ID compra: ")),
        int(input("ID produto: ")),
        int(input("Quantidade: ")),
        float(input("Preço unitário: ")),
        float(input("Valor total: "))
    ]
    cadastrar_item_compra(*args)
    print("✅ Item de compra registrado.")

def criar_venda_flow():
    print("Valores: produto_id,quantidade,valor_total,data_venda")
    args = [
        int(input("ID produto: ")),
        int(input("Quantidade: ")),
        float(input("Valor total: ")),
        datetime.strptime(input("Data (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M")
    ]
    registrar_venda(*args)
    print("✅ Venda registrada.")

def criar_item_venda_flow():
    print("Valores: id_venda,id_produto,quantidade,preco_unitario,desconto,valor_total")
    args = [
        int(input("ID venda: ")),
        int(input("ID produto: ")),
        int(input("Quantidade: ")),
        float(input("Preço unitário: ")),
        float(input("Desconto: ")),
        float(input("Valor total: "))
    ]
    cadastrar_item_venda(*args)
    print("✅ Item de venda registrado.")

def criar_estoque_flow():
    print("Valores: id_produto,id_loja,quantidade_atual,quantidade_minima,quantidade_maxima")
    args = [
        int(input("ID produto: ")),
        int(input("ID loja: ")),
        int(input("Qtde atual: ")),
        int(input("Qtde mínima: ")),
        int(input("Qtde máxima: "))
    ]
    cadastrar_estoque(*args)
    print("✅ Estoque cadastrado.")

def criar_promocao_flow():
    print("Valores: nome_promocao,descricao,data_inicio,data_fim,percentual_desconto,ativa")
    args = [
        input("Nome: "),
        input("Descrição: "),
        datetime.strptime(input("Início (YYYY-MM-DD): "), "%Y-%m-%d").date(),
        datetime.strptime(input("Fim    (YYYY-MM-DD): "), "%Y-%m-%d").date(),
        float(input("Desconto %: ")),
        True
    ]
    print("ID =", cadastrar_promocao(*args))

def criar_produto_promocao_flow():
    print("Valores: id_promocao,id_produto,preco_promocional")
    args = [
        int(input("ID promoção: ")),
        int(input("ID produto: ")),
        float(input("Preço promocional: "))
    ]
    cadastrar_produto_promocao(*args)
    print("✅ Produto em promoção registrado.")

if __name__ == "__main__":
    main()
