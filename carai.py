from ZODB import DB
from ZODB.FileStorage import FileStorage
import transaction
import persistent
import ZODB.broken
import types
from database.produto_repo import (
    Produto, Cliente, Loja,     
    inserir_produto_zodb,
    inserir_categoria_zodb,
    root
)

def print_zodb_tables(root):
    print("Tabelas disponíveis na ZODB:")
    for key in root.keys():
        print(f"- {key}")
        

def print_zodb_tree_completo(root):
    from rich.console import Console
    from rich.table import Table
    from BTrees.OOBTree import OOBTree
    from persistent.mapping import PersistentMapping
    console = Console()
    console.print("[bold underline green]Tabelas e dados da ZODB:[/]\n")
    
    for table_name, data in root.items():
        console.print(f"\n[bold magenta]Tabela:[/] [cyan]{table_name}[/]")

        # Tenta acessar os dados como se fosse um dicionário
        try:
            if isinstance(data, (dict, PersistentMapping, OOBTree)):
                entries = data.items()
            elif isinstance(data, (list, tuple)):
                entries = enumerate(data)
            else:
                console.print(f"[red]Tipo não iterável ou não suportado: {type(data)}[/]")
                console.print(repr(data))
                continue

            rich_table = Table(show_header=True, header_style="bold blue")
            rich_table.add_column("Chave/Índice", style="dim", width=12)
            rich_table.add_column("Valor", style="white")

            for k, v in entries:
                rich_table.add_row(str(k), repr(v))

            console.print(rich_table)

        except Exception as e:
            console.print(f"[red]Erro ao acessar dados da tabela '{table_name}': {e}[/]")

def print_zodb_tree(obj, indent=0, visited=None):
    if visited is None:
        visited = set()

    spacing = "  " * indent
    obj_id = id(obj)

    if obj_id in visited:
        print(f"{spacing}<Already Visited: {type(obj).__name__}>")
        return
    visited.add(obj_id)

    if isinstance(obj, dict):
        print(f"{spacing}Dict:")
        for k, v in obj.items():
            print(f"{spacing}  Key: {k}")
            print_zodb_tree(v, indent + 2, visited)

    elif isinstance(obj, (list, set, tuple)):
        print(f"{spacing}{type(obj).__name__} of length {len(obj)}:")
        for item in obj:
            print_zodb_tree(item, indent + 1, visited)

    elif isinstance(obj, persistent.Persistent):
        print(f"{spacing}Persistent Object: {type(obj).__name__}")
        attrs = vars(obj)
        for attr, val in attrs.items():
            print(f"{spacing}  .{attr} = ", end="")
            if isinstance(val, (dict, list, set, tuple, persistent.Persistent)):
                print()
                print_zodb_tree(val, indent + 2, visited)
            else:
                print(val)

    elif isinstance(obj, ZODB.broken.Broken):
        print(f"{spacing}<Broken Persistent Object>")

    else:
        print(f"{spacing}{repr(obj)}")

# Exemplo de uso
storage = FileStorage('zodb_storage.fs', read_only=True)
db = DB(storage)
connection = db.open()
root = connection.root()

print(">>> ZODB CONTENTS <<<")
print_zodb_tree(root)

connection.close()
db.close()
