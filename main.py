from datetime import datetime
from types import SimpleNamespace
from database.produto_repo import (
    Produto, Cliente, Loja,
    inserir_produto as inserir_zodb,
    fetch_todos_os_produtos, buscar_produto
)
from database.postgres import (
    criar_tabelas,
    # Categoria
    cadastrar_categoria, listar_categorias,
    # Produto
    cadastrar_produto, listar_produtos,
    # Cliente
    cadastrar_cliente, listar_clientes,
    # Loja
    cadastrar_loja, listar_lojas,
    # Funcionario
    cadastrar_funcionario, listar_funcionarios,
    # Fornecedor
    cadastrar_fornecedor, listar_fornecedores,
    # Compra
    cadastrar_compra, listar_compras,
    cadastrar_item_compra, listar_itens_compra,
    # Estoque
    atualizar_estoque, listar_estoque,
    # Venda
    registrar_venda, fetch_vendas_por_trimestre,
    # Comentario (Mongo)    
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

# Flows gerais seguem padrão CRUD para cada entidade

def flow_generic_insert(fields, insert_func, success_msg):
    data = {}
    for field, prompt in fields.items():
        data[field] = console.input(f"[cyan]{prompt}:[/] ")
    new_id = insert_func(**data)
    console.print(f"✅ {success_msg} #[bold]{new_id}[/bold]", style="green")

# ---------------- Categoria ----------------

def cadastrar_categoria_flow():
    flow_generic_insert(
        {'nome': 'Nome da categoria', 'descricao': 'Descrição (opcional)'},
        cadastrar_categoria,
        'Categoria criada'
    )

def listar_categoria_flow():
    rows = listar_categorias()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Descrição", style="white")
    for c in rows:
        table.add_row(str(c['id_categoria']), c['nome_categoria'], c.get('descricao',''))
    console.print(table)

# ---------------- Produto ----------------

def cadastrar_produto_flow():
    fields = {
        'codigo_produto': 'Código do produto',
        'nome_produto': 'Nome do produto',
        'descricao': 'Descrição (opcional)',
        'id_categoria': 'ID da categoria (opcional)',
        'marca': 'Marca (opcional)',
        'preco_atual': 'Preço R$' ,
        'unidade_medida': 'Unidade de medida (opcional)',
        'ativo': 'Ativo (True/False)'
    }
    data = {}
    for f,p in fields.items():
        val = console.input(f"[cyan]{p}:[/] ")
        data[f] = val or None
    # conversões
    data['id_categoria'] = int(data['id_categoria']) if data['id_categoria'] else None
    data['preco_atual'] = float(data['preco_atual'])
    data['ativo'] = data['ativo'].lower() in ('true','1','sim','s')
    p = Produto(**data)
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

# ---------------- Cliente ----------------

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
    rows = listar_clientes()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Email", style="white")
    for c in rows:
        table.add_row(str(c['id_cliente']), c['nome'], c['email'])
    console.print(table)

# ---------------- Loja ----------------

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
    rows = listar_lojas()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Cidade", style="white")
    for l in rows:
        table.add_row(str(l['id_loja']), l['nome_loja'], l['cidade'])
    console.print(table)

# ---------------- Funcionario ----------------

def cadastrar_funcionario_flow():
    data = {
        'codigo_funcionario': console.input("[cyan]Código funcionário:[/] "),
        'nome':                console.input("[cyan]Nome:[/] "),
        'cargo':               console.input("[cyan]Cargo:[/] "),
        'id_loja':             int(console.input("[cyan]ID loja:[/] ")),
        'salario':             float(console.input("[cyan]Salário:[/] ")),
        'ativo':               True
    }
    f = SimpleNamespace(**data)
    fid = cadastrar_funcionario(f)
    console.print(f"✅ Funcionário #[bold]{fid}[/bold] criado.", style="green")


def listar_funcionario_flow():
    rows = listar_funcionarios()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Cargo", style="white")
    table.add_column("Loja", style="white")
    for f in rows:
        table.add_row(str(f['id_funcionario']), f['nome'], f['cargo'], str(f['id_loja']))
    console.print(table)

# ---------------- Fornecedor ----------------

def cadastrar_fornecedor_flow():
    f = SimpleNamespace(
        cnpj          = console.input("[cyan]CNPJ:[/] "),
        razao_social  = console.input("[cyan]Razão social:[/] "),
        nome_fantasia = console.input("[cyan]Nome fantasia:[/] "),
        telefone      = console.input("[cyan]Telefone:[/] "),
        email         = console.input("[cyan]Email:[/] "),
        endereco      = console.input("[cyan]Endereço:[/] "),
        cidade        = console.input("[cyan]Cidade:[/] "),
        estado        = console.input("[cyan]Estado (UF):[/] "),
        ativo         = True
    )
    fid = cadastrar_fornecedor(f)
    console.print(f"✅ Fornecedor #[bold]{fid}[/bold] criado.", style="green")

def listar_fornecedor_flow():
    rows = listar_fornecedores()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Razão Social", style="white")
    table.add_column("Cidade", style="white")
    for f in rows:
        table.add_row(str(f['id_fornecedor']), f['razao_social'], f['cidade'])
    console.print(table)

# ---------------- Estoque ----------------

def atualizar_estoque_flow():
    e = {
      'id_produto':     int(console.input("[cyan]ID produto:[/] ")),
      'id_loja':        int(console.input("[cyan]ID loja:[/] ")),
      'quantidade_atual': int(console.input("[cyan]Qtd atual:[/] ")),
      'quantidade_minima': int(console.input("[cyan]Qtd mínima:[/] ")),
      'quantidade_maxima': int(console.input("[cyan]Qtd máxima:[/] "))
    }
    atualizar_estoque(e)
    console.print("✅ Estoque atualizado.", style="green")


def listar_estoque_flow():
    rows = listar_estoque()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Produto", style="cyan")
    table.add_column("Loja", style="white")
    table.add_column("Atual", style="white")
    table.add_column("Mínimo", style="white")
    table.add_column("Máximo", style="white")
    for e in rows:
        table.add_row(str(e['id_produto']), str(e['id_loja']), str(e['quantidade_atual']), str(e['quantidade_minima']), str(e['quantidade_maxima']))
    console.print(table)

# ---------------- Compra e Itens ----------------

def cadastrar_compra_flow():
    compra = {
        'numero_compra':  console.input("[cyan]Número compra:[/] "),
        'id_fornecedor':   int(console.input("[cyan]ID fornecedor:[/] ")),
        'id_loja':         int(console.input("[cyan]ID loja:[/] ")),
        'data_compra':     console.input("[cyan]Data (YYYY-MM-DD HH:MM:SS):[/] "),
        'valor_total':     float(console.input("[cyan]Valor total:[/] ")),
        'status_compra':   console.input("[cyan]Status:[/] ")
    }
    cid = cadastrar_compra(compra)
    console.print(f"✅ Compra #[bold]{cid}[/bold] registrada.", style="green")


def listar_compra_flow():
    rows = listar_compras()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Fornecedor", style="white")
    table.add_column("Loja", style="white")
    table.add_column("Data", style="white")
    table.add_column("Valor", style="white")
    for c in rows:
        table.add_row(str(c['id_compra']), str(c['id_fornecedor']), str(c['id_loja']), str(c['data_compra']), f"R$ {c['valor_total']}")
    console.print(table)

def cadastrar_item_compra_flow():
    item = {
        'id_compra':      int(console.input("[cyan]ID compra:[/] ")),
        'id_produto':     int(console.input("[cyan]ID produto:[/] ")),
        'quantidade':     int(console.input("[cyan]Quantidade:[/] ")),
        'preco_unitario': float(console.input("[cyan]Preço unitário:[/] "))
    }
    iid = cadastrar_item_compra(item)
    console.print(f"✅ Item de compra #[bold]{iid}[/bold] criado.", style="green")


def listar_itens_compra_flow():
    rows = listar_itens_compra()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Compra", style="cyan")
    table.add_column("Produto", style="white")
    table.add_column("Qtd", style="white")
    table.add_column("Valor total", style="white")
    for i in rows:
        table.add_row(str(i['id_compra']), str(i['id_produto']), str(i['quantidade']), f"R$ {i['valor_total']}")
    console.print(table)

# ---------------- Venda e Comentário ----------------

def registrar_venda_flow():
    registrar_venda(
        int(console.input("[cyan]ID produto:[/] ")),
        int(console.input("[cyan]Quantidade:[/] ")),
        float(console.input("[cyan]Valor total R$:[/] ")),
        datetime.strptime(console.input("[cyan]Data (YYYY-MM-DD):[/] "), "%Y-%m-%d")
    )
    console.print("✅ Venda registrada.", style="green")

def vendas_trimestre_flow():
    exibir_vendas_por_trimestre(fetch_vendas_por_trimestre())

def inserir_comentario_flow():
    inserir_comentario({
        'produto_id': int(console.input("[cyan]ID produto:[/] ")),
        'cliente': console.input("[cyan]Cliente:[/] "),
        'comentario': console.input("[cyan]Comentário:[/] "),
        'data': datetime.now().isoformat(),
        'imagens': [u.strip() for u in console.input("[cyan]URLs (vírgula):[/] ").split(',') if u.strip()]
    })
    console.print("✅ Comentário inserido.", style="green")

def listar_comentario_flow():
    pid = int(console.input("[cyan]ID produto para comentários:[/] "))
    rows = listar_comentarios(pid)
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Cliente", style="cyan")
    table.add_column("Data", style="white")
    table.add_column("Comentário", style="white")
    for c in rows:
        table.add_row(c['cliente'], c['data'], c['comentario'])
    console.print(table)

# ---------------- Menus ----------------

def create_submenu(title, options):
    while True:
        table = Table(title=title, show_header=False)
        table.add_column("Opção", style="cyan")
        table.add_column("Descrição", style="white")
        for key, (desc, _) in options.items():
            table.add_row(key, desc)
        console.print(Panel(table, border_style="blue"))
        choice = console.input(f"[bold green]Selecione em {title} (b para voltar):[/] ").strip().lower()
        if choice == 'b': break
        action = options.get(choice)
        if action: action[1]()
        else: console.print("Opção inválida.", style="bold red")

# Submenus dicts
submenu_categoria = {'1':('Cadastrar', cadastrar_categoria_flow),'2':('Listar', listar_categoria_flow),'b':('Voltar',None)}
submenu_produto   = {'1':('Cadastrar', cadastrar_produto_flow),'2':('Listar', listar_produto_flow),'b':('Voltar',None)}
submenu_cliente   = {'1':('Cadastrar', cadastrar_cliente_flow),'2':('Listar', listar_cliente_flow),'b':('Voltar',None)}
submenu_loja      = {'1':('Cadastrar', cadastrar_loja_flow),'2':('Listar', listar_loja_flow),'b':('Voltar',None)}
submenu_func      = {'1':('Cadastrar', cadastrar_funcionario_flow),'2':('Listar', listar_funcionario_flow),'b':('Voltar',None)}
submenu_fornec    = {'1':('Cadastrar', cadastrar_fornecedor_flow),'2':('Listar', listar_fornecedor_flow),'b':('Voltar',None)}
submenu_estoque   = {'1':('Atualizar', atualizar_estoque_flow),'2':('Listar', listar_estoque_flow),'b':('Voltar',None)}
submenu_compra    = {'1':('Registrar', cadastrar_compra_flow),'2':('Listar', listar_compra_flow),'b':('Voltar',None)}
submenu_itemcomp  = {'1':('Cadastrar item', cadastrar_item_compra_flow),'2':('Listar itens', listar_itens_compra_flow),'b':('Voltar',None)}
submenu_venda     = {'1':('Registrar', registrar_venda_flow),'2':('Por trimestre', vendas_trimestre_flow),'b':('Voltar',None)}
submenu_coment    = {'1':('Inserir', inserir_comentario_flow),'2':('Listar', listar_comentario_flow),'b':('Voltar',None)}

# Menu principal
COMMANDS = {
    'esquemas':('Criar esquemas', criar_esquemas),
    'categoria':('Menu categoria', lambda: create_submenu('Categoria', submenu_categoria)),
    'produto'  :('Menu produto', lambda: create_submenu('Produto', submenu_produto)),
    'cliente'  :('Menu cliente', lambda: create_submenu('Cliente', submenu_cliente)),
    'loja'     :('Menu loja', lambda: create_submenu('Loja', submenu_loja)),
    'funcionario':('Menu funcionário', lambda: create_submenu('Funcionario', submenu_func)),
    'fornecedor' :('Menu fornecedor', lambda: create_submenu('Fornecedor', submenu_fornec)),
    'estoque'  :('Menu estoque', lambda: create_submenu('Estoque', submenu_estoque)),
    'compra'   :('Menu compra', lambda: create_submenu('Compra', submenu_compra)),
    'itemcompra':('Menu item compra', lambda: create_submenu('ItemCompra', submenu_itemcomp)),
    'venda'    :('Menu venda', lambda: create_submenu('Venda', submenu_venda)),
    'comentario':('Menu comentário', lambda: create_submenu('Comentário', submenu_coment)),
    'sair'     :('Sair', lambda: exit())
}

def show_menu():
    table = Table(title="Menu de Comandos", show_header=True, header_style="bold blue")
    table.add_column("Comando", style="cyan")
    table.add_column("Descrição", style="white")
    for cmd,(desc,_) in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(Panel(table, title="Escolha uma opção", border_style="bright_blue"))


def main():
    while True:
        show_menu()
        cmd = console.input("[bold green]Digite um comando:[/] ").strip().lower()
        action = COMMANDS.get(cmd)
        if action: action[1]()
        else: console.print("Comando inválido.", style="bold red")

if __name__=='__main__':
    main()
