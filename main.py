from datetime import datetime
from database.produto_repo import (
    Produto, Cliente, Loja,
    inserir_produto as inserir_zodb,
    fetch_todos_os_produtos, buscar_produto
)
from database.postgres import (
    criar_tabelas, cadastrar_categoria, listar_categorias,
    cadastrar_produto, listar_produtos,
    cadastrar_cliente, listar_clientes,
    cadastrar_loja, listar_lojas,
    registrar_venda, fetch_vendas_por_trimestre
)
from database.mongo import inserir_comentario, listar_comentarios
from utils.analises import exibir_vendas_por_trimestre

# Biblioteca para menu mais bonito
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def criar_esquemas():
    criar_tabelas()
    console.print("✅ Esquemas criados.", style="bold green")

# Flows de Categoria

def cadastrar_categoria_flow():
    nome = console.input("[cyan]Nome da categoria:[/] ")
    desc = console.input("[cyan]Descrição (opcional):[/] ")
    cid = cadastrar_categoria(nome, desc)
    console.print(f"✅ Categoria #[bold]{cid}[/bold] criada.", style="green")


def listar_categoria_flow():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Nome", style="white")
    table.add_column("Descrição", style="white")
    for c in listar_categorias():
        table.add_row(str(c['id_categoria']), c['nome_categoria'], c.get('descricao',''))
    console.print(table)

# Flows de Produto

def cadastrar_produto_flow():
    codigo = console.input("[cyan]Código do produto:[/] ")
    nome = console.input("[cyan]Nome do produto:[/] ")
    desc = console.input("[cyan]Descrição (opcional):[/] ")
    id_cat = console.input("[cyan]ID da categoria (opcional):[/] ")
    marca = console.input("[cyan]Marca (opcional):[/] ")
    preco = float(console.input("[cyan]Preço R$:[/] "))
    unidade = console.input("[cyan]Unidade de medida (opcional):[/] ")
    ativo = True
    p = Produto(
        codigo_produto=codigo,
        nome_produto=nome,
        descricao=desc or None,
        id_categoria=int(id_cat) if id_cat else None,
        marca=marca or None,
        preco_atual=preco,
        unidade_medida=unidade or None,
        ativo=ativo
    )
    pid = cadastrar_produto(p)
    zid = inserir_zodb(p)
    console.print(f"✅ Produto SQL #[bold]{pid}[/bold] / ZODB #[bold]{zid}[/bold]", style="green")


def listar_produto_flow():
    produtos = listar_produtos()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Código", style="white")
    table.add_column("Nome", style="white")
    table.add_column("Preço", style="white")
    for p in produtos:
        table.add_row(str(p['id_produto']), p['codigo_produto'], p['nome_produto'], f"R$ {p['preco_atual']}")
    console.print(table)

# Flows de Cliente

def cadastrar_cliente_flow():
    c = Cliente(
        cpf=console.input("[cyan]CPF:[/] "),
        nome=console.input("[cyan]Nome:[/] "),
        email=console.input("[cyan]Email:[/] "),
        telefone=console.input("[cyan]Telefone:[/] "),
        endereco=console.input("[cyan]Endereço:[/] "),
        cidade=console.input("[cyan]Cidade:[/] "),
        estado=console.input("[cyan]Estado (UF):[/] "),
        cep=console.input("[cyan]CEP:[/] "),
        ativo=True
    )
    cid = cadastrar_cliente(c)
    console.print(f"✅ Cliente #[bold]{cid}[/bold] cadastrado.", style="green")


def listar_cliente_flow():
    clientes = listar_clientes()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Email", style="white")
    for c in clientes:
        table.add_row(str(c['id_cliente']), c['nome'], c['email'])
    console.print(table)

# Flows de Loja

def cadastrar_loja_flow():
    l = Loja(
        codigo_loja=console.input("[cyan]Código loja:[/] "),
        nome_loja=console.input("[cyan]Nome loja:[/] "),
        endereco=console.input("[cyan]Endereço:[/] "),
        cidade=console.input("[cyan]Cidade:[/] "),
        estado=console.input("[cyan]Estado (UF):[/] "),
        cep=console.input("[cyan]CEP:[/] "),
        telefone=console.input("[cyan]Telefone:[/] "),
        gerente=console.input("[cyan]Gerente:[/] "),
        ativa=True
    )
    lid = cadastrar_loja(l)
    console.print(f"✅ Loja #[bold]{lid}[/bold] cadastrada.", style="green")


def listar_loja_flow():
    lojas = listar_lojas()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Cidade", style="white")
    for l in lojas:
        table.add_row(str(l['id_loja']), l['nome_loja'], l['cidade'])
    console.print(table)

# Flows de Venda

def registrar_venda_flow():
    pid = int(console.input("[cyan]ID produto:[/] "))
    qtd = int(console.input("[cyan]Quantidade:[/] "))
    total = float(console.input("[cyan]Valor total R$:[/] "))
    data = datetime.strptime(console.input("[cyan]Data (YYYY-MM-DD):[/] "), "%Y-%m-%d")
    registrar_venda(pid, qtd, total, data)
    console.print("✅ Venda registrada.", style="green")


def vendas_trimestre_flow():
    exibir_vendas_por_trimestre(fetch_vendas_por_trimestre())

# Flows de Comentário

def inserir_comentario_flow():
    cid = int(console.input("[cyan]ID produto:[/] "))
    entry = {
        'produto_id': cid,
        'cliente': console.input("[cyan]Cliente:[/] "),
        'comentario': console.input("[cyan]Comentário:[/] "),
        'data': datetime.now().isoformat(),
        'imagens': [u.strip() for u in console.input("[cyan]URLs (vírgula):[/] ").split(',') if u.strip()]
    }
    inserir_comentario(entry)
    console.print("✅ Comentário inserido.", style="green")


def listar_comentario_flow():
    pid = int(console.input("[cyan]ID produto para comentários:[/] "))
    coms = listar_comentarios(pid)
    if not coms:
        console.print(f"Nenhum comentário para #[bold]{pid}[/bold].", style="red")
        return
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Cliente", style="cyan")
    table.add_column("Data", style="white")
    table.add_column("Comentário", style="white")
    for c in coms:
        table.add_row(c['cliente'], c['data'], c['comentario'])
    console.print(table)

# Função genérica para submenus

def create_submenu(title, options):
    while True:
        table = Table(title=title, show_header=False)
        table.add_column("Opção", style="cyan", no_wrap=True)
        table.add_column("Descrição", style="white")
        for key, (desc, _) in options.items():
            table.add_row(key, desc)
        console.print(Panel(table, border_style="blue"))
        choice = console.input(f"[bold green]Selecione opção em {title} (b para voltar):[/] ").strip().lower()
        if choice == 'b':
            break
        action = options.get(choice)
        if action and action[1]:
            action[1]()
        else:
            console.print("Opção inválida.", style="bold red")

# Definição de submenus
submenu_categoria = {
    '1': ('Cadastrar categoria', cadastrar_categoria_flow),
    '2': ('Listar categorias', listar_categoria_flow),
    'b': ('Voltar', None)
}
submenu_produto = {
    '1': ('Cadastrar produto', cadastrar_produto_flow),
    '2': ('Listar produtos', listar_produto_flow),
    'b': ('Voltar', None)
}
submenu_cliente = {
    '1': ('Cadastrar cliente', cadastrar_cliente_flow),
    '2': ('Listar clientes', listar_cliente_flow),
    'b': ('Voltar', None)
}
submenu_loja = {
    '1': ('Cadastrar loja', cadastrar_loja_flow),
    '2': ('Listar lojas', listar_loja_flow),
    'b': ('Voltar', None)
}
submenu_venda = {
    '1': ('Registrar venda', registrar_venda_flow),
    '2': ('Vendas por trimestre', vendas_trimestre_flow),
    'b': ('Voltar', None)
}
submenu_comentario = {
    '1': ('Inserir comentário', inserir_comentario_flow),
    '2': ('Listar comentários', listar_comentario_flow),
    'b': ('Voltar', None)
}

# Menu principal
COMMANDS = {
    'esquemas': ('Criar esquemas', criar_esquemas),
    'categoria': ('Menu categoria', lambda: create_submenu('Categoria', submenu_categoria)),
    'produto': ('Menu produto', lambda: create_submenu('Produto', submenu_produto)),
    'cliente': ('Menu cliente', lambda: create_submenu('Cliente', submenu_cliente)),
    'loja': ('Menu loja', lambda: create_submenu('Loja', submenu_loja)),
    'venda': ('Menu venda', lambda: create_submenu('Venda', submenu_venda)),
    'comentario': ('Menu comentário', lambda: create_submenu('Comentário', submenu_comentario)),
    'sair': ('Sair do programa', lambda: exit())
}

def show_menu():
    table = Table(title="Menu de Comandos", show_header=True, header_style="bold blue")
    table.add_column("Comando", style="cyan", no_wrap=True)
    table.add_column("Descrição", style="white")
    for cmd, (desc, _) in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(Panel(table, title="Escolha uma opção", border_style="bright_blue"))


def main():
    while True:
        show_menu()
        cmd = console.input("[bold green]Digite um comando:[/] ").strip().lower()
        action = COMMANDS.get(cmd)
        if action:
            action[1]()
        else:
            console.print("Comando inválido. Tente novamente.", style="bold red")

if __name__ == '__main__':
    main()
