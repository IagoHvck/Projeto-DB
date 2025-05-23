# main.py
from datetime import datetime
from database.mongo     import inserir_comentario, listar_comentarios
from database.produto_repo import inserir_produto as inserir_produto_zodb
from modelos.produto    import Produto
from utils.analises     import exibir_vendas_por_trimestre, exibir_comentarios
from database.postgres \
    import criar_tabelas, \
           inserir_produto   as inserir_produto_sql, \
           registrar_venda, \
           fetch_vendas_por_trimestre


def menu():
    print("""
1) Criar esquemas
2) Cadastrar produto
3) Registrar venda
4) Vendas por trimestre
5) Inserir comentário (NoSQL)
6) Listar comentários
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
            nome  = input("Nome: ")
            cat   = input("Categoria: ")
            marca = input("Marca: ")
            preco = float(input("Preço: "))
            est   = int(input("Estoque inicial: "))
            p = Produto(nome, cat, marca, preco, est)
            # primeiro grava no PostgreSQL
            pid_sql = inserir_produto_sql(p)
            p.id = pid_sql
            # depois grava no ZODB
            pid_zodb = inserir_produto_zodb(p)
            print(f"✅ Produto cadastrado: SQL_ID={pid_sql}, ZODB_ID={pid_zodb} → {p}\n")
        elif opt == "3":
            pid   = int(input("ID do produto: "))
            qtd   = int(input("Quantidade vendida: "))
            total = float(input("Valor total R$ "))
            data  = input("Data (YYYY-MM-DD): ")
            registrar_venda(pid, qtd, total, data)
            print("✅ Venda registrada.\n")
        elif opt == "4":
            vendas = fetch_vendas_por_trimestre()
            exibir_vendas_por_trimestre(vendas)
            print()
        elif opt == "5":
            pid  = int(input("ID do produto: "))
            cli  = input("Cliente: ")
            com  = input("Comentário: ")

            raw = input("Data (YYYY-MM-DD): ")
            try:
                from datetime import datetime
                data_date = datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Data inválida! Use YYYY-MM-DD.\n")
                continue

            imgs = input("URLs de imagens (vírgula-separadas): ").split(",")
            payload = {
                "produto_id": pid,
                "cliente":    cli,
                "comentario": com,
                # converte date em string ISO (BSON aceita)
                "data":       data_date.isoformat(),
                "imagens":    [u.strip() for u in imgs if u.strip()]
            }
            inserir_comentario(payload)
            print("✅ Comentário inserido.\n")
        elif opt == "6":
            pid = int(input("ID do produto para buscar comentários: "))
            coms = listar_comentarios(pid)
            exibir_comentarios(coms)
            print()
        elif opt == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida.\n")

if __name__ == "__main__":
    main()
