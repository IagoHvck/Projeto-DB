import os
from ingestao import cria_bancos, popula_operacional, popula_dw, popula_nosql
from analise import vendas_por_trimestre, comentarios_do_produto

def debug_paths():
    cwd = os.getcwd()
    db_dir = os.path.join(cwd, "database")
    print(f"CWD: {cwd}")
    if os.path.isdir(db_dir):
        print(f"Conteúdo de '{db_dir}':")
        for f in os.listdir(db_dir):
            print("  ", f)
    else:
        print(f"❌ Pasta esperada não encontrada: {db_dir}")

def menu():
    print()
    print("1) Criar esquemas")
    print("2) Popular operacional")
    print("3) Popular DW")
    print("4) Popular NoSQL")
    print("5) Vendas por trimestre")
    print("6) Comentários de produto")
    print("0) Sair")

def main():
    # debug inicial
    debug_paths()

    while True:
        menu()
        cmd = input("> ").strip()
        if cmd == "1":
            cria_bancos()
        elif cmd == "2":
            popula_operacional()
            print("✅ Operacional populado.")
        elif cmd == "3":
            popula_dw()
            print("✅ DW populado.")
        elif cmd == "4":
            popula_nosql()
            print("✅ NoSQL populado.")
        elif cmd == "5":
            for r in vendas_por_trimestre():
                print(r)
        elif cmd == "6":
            try:
                pid = int(input("ID do produto? "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            for c in comentarios_do_produto(pid):
                print(c)
        elif cmd == "0":
            print("Saindo…")
            break
        else:
            print("Opção inválida. Digite 0–6.")

if __name__ == "__main__":
    main()
