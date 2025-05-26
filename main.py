# main.py
from datetime import datetime
from database.produto_repo import (
    Produto, Cliente, Loja,
    inserir_produto as inserir_produto_zodb,
    fetch_todos_os_produtos, buscar_produto
)
from database.postgres import (
    criar_tabelas,
    cadastrar_categoria, listar_categorias,
    cadastrar_produto, listar_produtos,
    cadastrar_cliente, listar_clientes,
    cadastrar_loja, listar_lojas,
    registrar_venda, fetch_vendas_por_trimestre
)
from database.mongo import inserir_comentario, listar_comentarios
from utils.analises import exibir_vendas_por_trimestre, exibir_comentarios

def menu():
    print("""
1) Criar esquemas
2) Cadastrar categoria
3) Cadastrar produto
4) Listar produtos
5) Cadastrar cliente
6) Listar clientes
7) Cadastrar loja
8) Listar lojas
9) Registrar venda
10) Vendas por trimestre
11) Inserir comentário (NoSQL)
12) Listar comentários
0) Sair
""")

def main():
    while True:
        menu()
        opt = input("> ").strip()

        if opt == "1":
            criar_tabelas()
            print("✅ Esquemas criados.\n")

        elif opt == "2":
            nome = input("Nome da categoria: ")
            desc = input("Descrição (opcional): ")
            cid = cadastrar_categoria(nome, desc)
            print(f"✅ Categoria #{cid} criada.\n")
            cats = listar_categorias()
            print("\n📋 Categorias cadastradas:")
            for c in cats:
                print(f"  [{c['id_categoria']}] {c['nome_categoria']}"
                      f"{' – ' + c['descricao'] if c['descricao'] else ''}")
            print()

        elif opt == "3":
            pid = cadastrar_produto(p)
            zid = inserir_produto_zodb(p)
            print(f"✅ Produto SQL #{pid} / ZODB #{zid}\n")

        elif opt == "4":

            #O print é muito feio.
            #print("Produtos SQL:", listar_produtos())
            print("Produtos ZODB:", fetch_todos_os_produtos(), "\n")

        elif opt == "5":
            c = Cliente(
                cpf      = input("CPF: "),
                nome     = input("Nome: "),
                email    = input("Email: "),
                telefone = input("Telefone: "),
                endereco = input("Endereço: "),
                cidade   = input("Cidade: "),
                estado   = input("Estado (UF): "),
                cep      = input("CEP: "),
                ativo    = True
            )
            cid = cadastrar_cliente(c)
            print(f"✅ Cliente #{cid} cadastrado.\n")

        elif opt == "6":
            print("Clientes:", listar_clientes(), "\n")

        elif opt == "7":
            l = Loja(
                codigo_loja = input("Código loja: "),
                nome_loja   = input("Nome loja: "),
                endereco    = input("Endereço: "),
                cidade      = input("Cidade: "),
                estado      = input("Estado: "),
                cep         = input("CEP: "),
                telefone    = input("Telefone: "),
                gerente     = input("Gerente: "),
                ativa       = True
            )
            lid = cadastrar_loja(l)
            print(f"✅ Loja #{lid} cadastrada.\n")

        elif opt == "8":
            print("Lojas:", listar_lojas(), "\n")

        elif opt == "9":
            pid   = int(input("ID produto: "))
            qtd   = int(input("Quantidade: "))
            total = float(input("Valor total R$ "))
            data  = datetime.strptime(input("Data (YYYY-MM-DD): "), "%Y-%m-%d")
            registrar_venda(pid, qtd, total, data)
            print("✅ Venda registrada.\n")

        elif opt == "10":
            exibir_vendas_por_trimestre(fetch_vendas_por_trimestre())
            print()

        elif opt == "11":
            pid  = int(input("ID produto: "))
            cli  = input("Cliente: ")
            com  = input("Comentário: ")
            data = datetime.now().isoformat()
            urls = input("URLs de imagens (vírgula): ").split(",")
            inserir_comentario({
                "produto_id": pid,
                "cliente":    cli,
                "comentario": com,
                "data":       data,
                "imagens":    [u.strip() for u in urls if u.strip()]
            })
            print("✅ Comentário inserido.\n")

        elif opt == "12":
            pid = int(input("ID do produto para ver comentários: "))
            coms = listar_comentarios(pid)
            if not coms:
                print(f"\nNenhum comentário encontrado para o produto #{pid}.\n")
            else:
                print(f"\n💬 Comentários do produto #{pid}:")
                for c in coms:
                    print(
                        f"  • {c['cliente']} em {c['data']}: “{c['comentario']}”\n"
                        f"    Imagens: {', '.join(c.get('imagens', [])) or 'nenhuma'}"
                    )
                print()

        elif opt == "0":
            print("Até mais!") 
            break

        else:
            print("Opção inválida.\n")

if __name__ == "__main__":
    main()
