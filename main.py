from ZODB import FileStorage, DB
import transaction
import ZODB
from datetime import datetime
from database.produto_repo import replicar_para_zodb
from database.produto_repo import inserir_produto_zodb
from database.migrator import migrar_tudo_para_zodb
from database.postgres import conectar
from types import SimpleNamespace
from database.produto_repo import (
    Produto, Cliente, Loja, Funcionario, 
    inserir_produto_zodb,
    inserir_categoria_zodb,
    root
)
from carai import print_zodb_tree, print_zodb_tables, print_zodb_tree_completo
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

def popular():
    inserts = [
        # Categorias
        ("INSERT INTO categoria (nome_categoria, descricao) VALUES (%s,%s);",
         [
             ('Eletrônicos', 'Produtos eletrônicos, tecnologia e informática'),
             ('Alimentos e Bebidas', 'Produtos alimentícios, bebidas e snacks'),
             ('Vestuário', 'Roupas, calçados e acessórios'),
             ('Casa e Decoração', 'Móveis, decoração e utilidades domésticas'),
             ('Esportes e Lazer', 'Produtos esportivos e equipamentos de lazer'),
             ('Beleza e Cuidados', 'Cosméticos, perfumaria e cuidados pessoais'),
             ('Livros e Papelaria', 'Livros, material escolar e escritório'),
             ('Brinquedos', 'Brinquedos e jogos infantis'),
         ]),
        # Produtos (exemplo para alguns; adicione todos da sua lista)
        ("INSERT INTO produto (codigo_produto, nome_produto, descricao, id_categoria, marca, preco_atual, unidade_medida) "
         "VALUES (%s,%s,%s,%s,%s,%s,%s);",
         [
             ('ELET001', 'Smartphone Galaxy S22', 'Smartphone Samsung Galaxy S22 128GB', 1, 'Samsung', 3499.00, 'UN'),
             ('ELET002', 'Notebook Dell Inspiron 15', 'Notebook Dell i5 8GB RAM 512GB SSD', 1, 'Dell', 2899.00, 'UN'),
             ('ELET001', 'Smartphone Galaxy S22', 'Smartphone Samsung Galaxy S22 128GB', 1, 'Samsung', 3499.00, 'UN'),
             ('ELET002', 'Notebook Dell Inspiron 15', 'Notebook Dell i5 8GB RAM 512GB SSD', 1, 'Dell', 2899.00, 'UN'),
             ('ELET003', 'TV Smart 50" 4K', 'Smart TV LG 50 polegadas 4K', 1, 'LG', 2199.00, 'UN'),
             ('ELET004', 'Fone Bluetooth', 'Fone de ouvido bluetooth JBL', 1, 'JBL', 249.90, 'UN'),
             ('ELET005', 'Mouse Gamer', 'Mouse gamer RGB Logitech', 1, 'Logitech', 199.90, 'UN'),
             
             #-- Alimentos e Bebidas
             ('ALIM001', 'Café Premium 500g', 'Café torrado e moído premium', 2, 'Melitta', 24.90, 'PCT'),
             ('ALIM002', 'Chocolate ao Leite 200g', 'Chocolate ao leite Nestlé', 2, 'Nestlé', 8.90, 'UN'),
             ('ALIM003', 'Água Mineral 1,5L', 'Água mineral sem gás', 2, 'Crystal', 2.90, 'UN'),
             ('ALIM004', 'Biscoito Integral', 'Biscoito integral multigrãos', 2, 'Vitarella', 4.50, 'PCT'),
             ('ALIM005', 'Suco Natural 1L', 'Suco de laranja natural', 2, 'Del Valle', 7.90, 'UN'),
             
             #-- Vestuário
             ('VEST001', 'Camisa Polo Masculina', 'Camisa polo algodão masculina', 3, 'Lacoste', 189.90, 'UN'),
             ('VEST002', 'Calça Jeans Feminina', 'Calça jeans feminina skinny', 3, 'Levi\'s', 259.90, 'UN'),
             ('VEST003', 'Tênis Running', 'Tênis para corrida unissex', 3, 'Nike', 399.90, 'PAR'),
             ('VEST004', 'Vestido Casual', 'Vestido casual feminino', 3, 'Renner', 119.90, 'UN'),
             ('VEST005', 'Mochila Escolar', 'Mochila escolar resistente', 3, 'Samsonite', 149.90, 'UN'),
             
             #-- Casa e Decoração
             ('CASA001', 'Jogo de Panelas 5 peças', 'Jogo de panelas antiaderente', 4, 'Tramontina', 299.90, 'JG'),
             ('CASA002', 'Edredom Casal', 'Edredom casal 100% algodão', 4, 'Santista', 189.90, 'UN'),
             ('CASA003', 'Conjunto de Toalhas', 'Kit 4 toalhas de banho', 4, 'Karsten', 99.90, 'KIT'),
             ('CASA004', 'Luminária de Mesa', 'Luminária LED para mesa', 4, 'Philips', 89.90, 'UN'),
             ('CASA005', 'Organizador Multiuso', 'Organizador plástico com divisórias', 4, 'Ordene', 39.90, 'UN'),
             
             #-- Esportes e Lazer
             ('ESPO001', 'Bola de Futebol', 'Bola de futebol oficial', 5, 'Adidas', 129.90, 'UN'),
             ('ESPO002', 'Kit Halteres 10kg', 'Par de halteres ajustáveis', 5, 'Kikos', 199.90, 'KIT'),
             ('ESPO003', 'Tapete Yoga', 'Tapete para yoga antiderrapante', 5, 'Acte Sports', 79.90, 'UN'),
             ('ESPO004', 'Bicicleta Aro 29', 'Mountain bike aro 29', 5, 'Caloi', 1499.00, 'UN'),
             ('ESPO005', 'Corda de Pular', 'Corda de pular profissional', 5, 'Speedo', 39.90, 'UN'),
             
             #-- Beleza e Cuidados
             ('BELZ001', 'Shampoo 400ml', 'Shampoo hidratante', 6, 'Pantene', 18.90, 'UN'),
             ('BELZ002', 'Creme Hidratante 200ml', 'Creme hidratante corporal', 6, 'Nivea', 24.90, 'UN'),
             ('BELZ003', 'Perfume Masculino 100ml', 'Perfume masculino amadeirado', 6, 'Boticário', 189.90, 'UN'),
             ('BELZ004', 'Base Líquida', 'Base líquida cobertura média', 6, 'MAC', 249.90, 'UN'),
             ('BELZ005', 'Kit Maquiagem', 'Kit maquiagem completo', 6, 'Ruby Rose', 89.90, 'KIT'),
             
             #-- Livros e Papelaria
             ('LIVR001', 'Livro Best Seller', 'Romance contemporâneo', 7, 'Intrínseca', 49.90, 'UN'),
             ('LIVR002', 'Caderno Universitário', 'Caderno 200 folhas', 7, 'Tilibra', 24.90, 'UN'),
             ('LIVR003', 'Kit Canetas Coloridas', 'Kit 12 canetas coloridas', 7, 'BIC', 19.90, 'KIT'),
             ('LIVR004', 'Agenda 2024', 'Agenda executiva 2024', 7, 'Foroni', 34.90, 'UN'),
             ('LIVR005', 'Calculadora Científica', 'Calculadora científica completa', 7, 'Casio', 89.90, 'UN'),
             
             #-- Brinquedos
             ('BRIN001', 'Lego Classic 500 peças', 'Kit Lego construção classic', 8, 'Lego', 299.90, 'CX'),
             ('BRIN002', 'Boneca Fashion', 'Boneca fashion com acessórios', 8, 'Mattel', 149.90, 'UN'),
             ('BRIN003', 'Quebra-cabeça 1000 peças', 'Quebra-cabeça paisagem', 8, 'Grow', 59.90, 'CX'),
             ('BRIN004', 'Carrinho Hot Wheels', 'Carrinho colecionável', 8, 'Hot Wheels', 12.90, 'UN'),
             ('BRIN005', 'Jogo de Tabuleiro', 'Jogo War clássico', 8, 'Grow', 89.90, 'CX'),
         ]),
        ("INSERT INTO loja (codigo_loja, nome_loja, endereco, cidade, estado, cep, telefone, gerente) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
         [
            ('LJ001', 'Loja Shopping Center', 'Av. Paulista, 1500', 'São Paulo', 'SP', '01310100', '11-3456-7890', 'Carlos Silva'),
            ('LJ002', 'Loja Barra Shopping', 'Av. das Américas, 4666', 'Rio de Janeiro', 'RJ', '22640102', '21-2431-8900', 'Ana Santos'),
            ('LJ003', 'Loja BH Shopping', 'Rod. BR-356, 3049', 'Belo Horizonte', 'MG', '31150900', '31-3456-7890', 'Pedro Oliveira'),
            ('LJ004', 'Loja Recife Shopping', 'Av. Agamenon Magalhães, 1000', 'Recife', 'PE', '52070000', '81-3456-7890', 'Maria Costa'),
            ('LJ005', 'Loja Salvador Shopping', 'Av. Tancredo Neves, 2915', 'Salvador', 'BA', '41820021', '71-3456-7890', 'João Pereira'),
            ('LJ006', 'Loja Porto Alegre', 'Av. Diário de Notícias, 300', 'Porto Alegre', 'RS', '90810000', '51-3456-7890', 'Paula Lima'),
            ('LJ007', 'Loja Brasília Shopping', 'SCN Q 6 L 2', 'Brasília', 'DF', '70716900', '61-3456-7890', 'Roberto Alves'),
            ('LJ008', 'Loja Curitiba Shopping', 'Av. das Torres, 1700', 'Curitiba', 'PR', '82840730', '41-3456-7890', 'Juliana Martins'),
         ]),

         #
        ("INSERT INTO funcionario (codigo_funcionario, nome, cargo, id_loja, salario) VALUES (%s,%s,%s,%s,%s);",
         [
            ('FUNC001', 'Carlos Silva', 'Gerente', 1, 8000.00),
            ('FUNC002', 'Mariana Rocha', 'Vendedor', 1, 2500.00),
            ('FUNC003', 'José Santos', 'Vendedor', 1, 2500.00),
            ('FUNC004', 'Laura Ferreira', 'Caixa', 1, 2200.00),


            ('FUNC005', 'Ana Santos', 'Gerente', 2, 8000.00),
            ('FUNC006', 'Bruno Costa', 'Vendedor', 2, 2500.00),
            ('FUNC007', 'Carla Almeida', 'Vendedor', 2, 2500.00),
            ('FUNC008', 'Diego Pereira', 'Caixa', 2, 2200.00),


            ('FUNC009', 'Pedro Oliveira', 'Gerente', 3, 8000.00),
            ('FUNC010', 'Fernanda Lima', 'Vendedor', 3, 2500.00),
            ('FUNC011', 'Ricardo Silva', 'Vendedor', 3, 2500.00),
            ('FUNC012', 'Tatiana Souza', 'Caixa', 3, 2200.00),


            ('FUNC013', 'Maria Costa', 'Gerente', 4, 8000.00),
            ('FUNC014', 'Anderson Melo', 'Vendedor', 4, 2500.00),
            ('FUNC015', 'Beatriz Nunes', 'Vendedor', 4, 2500.00),
            ('FUNC016', 'Cláudio Ribeiro', 'Caixa', 4, 2200.00),

            ('FUNC017', 'João Pereira', 'Gerente', 5, 8000.00),
            ('FUNC018', 'Sandra Matos', 'Vendedor', 5, 2500.00),
            ('FUNC019', 'Marcos Dias', 'Vendedor', 5, 2500.00),
            ('FUNC020', 'Elaine Barros', 'Caixa', 5, 2200.00),
         ]),
    ]
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            for sql, params_list in inserts:
                cur.executemany(sql, params_list)
    conn.close()
    migrar_tudo_para_zodb()      # sincroniza tudo do Postgres → ZODB

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
    # 1) coleta dos dados
    fields = {
        'codigo_produto': 'Código do produto',
        'nome_produto':   'Nome do produto',
        'descricao':      'Descrição (opcional)',
        'id_categoria':   'ID da categoria (opcional)',
        'marca':          'Marca (opcional)',
        'preco_atual':    'Preço R$',
        'unidade_medida': 'Unidade de medida (opcional)',
        'ativo':          'Ativo (True/False)'
    }
    data = {}
    for f, prompt in fields.items():
        val = console.input(f"[cyan]{prompt}:[/] ")
        data[f] = val or None

    # 2) conversões de tipo
    data['id_categoria'] = int(data['id_categoria']) if data['id_categoria'] else None
    data['preco_atual']  = float(data['preco_atual'])
    data['ativo']        = data['ativo'].lower() in ('true', '1', 'sim', 's')

    # 3) instancia o domínio Produto
    p = Produto(**data)

    # 4) persiste no PostgreSQL
    pid = cadastrar_produto(p)
    p.id = pid  # atribui o ID gerado

    # 5) garante que a categoria exista no ZODB
    if p.id_categoria is not None and p.id_categoria not in root['categorias']:
        # busca descrição no Postgres para manter consistência
        desc = None
        for c in listar_categorias():
            if c['id_categoria'] == p.id_categoria:
                desc = c.get('descricao')
                break
        inserir_categoria_zodb(p.id_categoria, desc)

    # 6) persiste no ZODB
    zid = inserir_produto_zodb(p)

    console.print(
        f"✅ Produto cadastrado:\n"
        f"   • SQL ID: [bold]{pid}[/bold]\n"
        f"   • ZODB ID: [bold]{zid}[/bold]\n"
        f"   • {p}\n",
        style="green"
    )

def get_zodb_root():
    storage = FileStorage.FileStorage('zodb_storage.fs', read_only=True)
    db = DB(storage)
    connection = db.open()
    root = connection.root()
    return root

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

    root = get_zodb_root()
    print_zodb_tree(root)
    print_zodb_tables(root)
    print_zodb_tree_completo(root)

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
    'popular':('Popular os Esquemas', popular),
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
