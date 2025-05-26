import psycopg2
from psycopg2.extras import RealDictCursor
from config import POSTGRES

def conectar():
    return psycopg2.connect(**POSTGRES)

def criar_tabelas():
    sql = """
    -- Categorias
    CREATE TABLE IF NOT EXISTS categoria (
      id_categoria   SERIAL PRIMARY KEY,
      nome_categoria VARCHAR(50) NOT NULL,
      descricao      TEXT
    );
    -- Produtos
    CREATE TABLE IF NOT EXISTS produto (
      id_produto     SERIAL PRIMARY KEY,
      codigo_produto VARCHAR(20) UNIQUE NOT NULL,
      nome_produto   VARCHAR(100) NOT NULL,
      descricao      TEXT,
      id_categoria   INT REFERENCES categoria(id_categoria),
      marca          VARCHAR(50),
      preco_atual    DECIMAL(10,2),
      unidade_medida VARCHAR(20),
      ativo          BOOLEAN DEFAULT TRUE
    );
    -- Clientes
    CREATE TABLE IF NOT EXISTS cliente (
      id_cliente SERIAL PRIMARY KEY,
      cpf        VARCHAR(11) UNIQUE NOT NULL,
      nome       VARCHAR(100) NOT NULL,
      email      VARCHAR(100),
      telefone   VARCHAR(20),
      endereco   VARCHAR(200),
      cidade     VARCHAR(50),
      estado     CHAR(2),
      cep        VARCHAR(8),
      ativo      BOOLEAN DEFAULT TRUE
    );
    -- Lojas
    CREATE TABLE IF NOT EXISTS loja (
      id_loja     SERIAL PRIMARY KEY,
      codigo_loja VARCHAR(10) UNIQUE NOT NULL,
      nome_loja   VARCHAR(50) NOT NULL,
      endereco    VARCHAR(200),
      cidade      VARCHAR(50),
      estado      CHAR(2),
      cep         VARCHAR(8),
      telefone    VARCHAR(20),
      gerente     VARCHAR(100),
      ativa       BOOLEAN DEFAULT TRUE
    );
    -- Funcionários
    CREATE TABLE IF NOT EXISTS funcionario (
      id_funcionario     SERIAL PRIMARY KEY,
      codigo_funcionario VARCHAR(10) UNIQUE NOT NULL,
      nome               VARCHAR(100) NOT NULL,
      cargo              VARCHAR(50),
      id_loja            INT REFERENCES loja(id_loja),
      salario            DECIMAL(10,2),
      ativo              BOOLEAN DEFAULT TRUE
    );
    -- Fornecedores
    CREATE TABLE IF NOT EXISTS fornecedor (
      id_fornecedor SERIAL PRIMARY KEY,
      cnpj           VARCHAR(14) UNIQUE NOT NULL,
      razao_social   VARCHAR(100) NOT NULL,
      nome_fantasia  VARCHAR(100),
      telefone       VARCHAR(20),
      email          VARCHAR(100),
      endereco       VARCHAR(200),
      cidade         VARCHAR(50),
      estado         CHAR(2),
      ativo          BOOLEAN DEFAULT TRUE
    );
    -- Compras e Itens
    CREATE TABLE IF NOT EXISTS compra (
      id_compra     SERIAL PRIMARY KEY,
      numero_compra VARCHAR(20) UNIQUE NOT NULL,
      id_fornecedor INT REFERENCES fornecedor(id_fornecedor),
      id_loja       INT REFERENCES loja(id_loja),
      data_compra   TIMESTAMP,
      valor_total   DECIMAL(12,2),
      status_compra VARCHAR(20)
    );
    CREATE TABLE IF NOT EXISTS item_compra (
      id_item       SERIAL PRIMARY KEY,
      id_compra     INT REFERENCES compra(id_compra),
      id_produto    INT REFERENCES produto(id_produto),
      quantidade    INT,
      preco_unitario DECIMAL(10,2),
      valor_total   DECIMAL(12,2)
    );
    -- Estoque
    CREATE TABLE IF NOT EXISTS estoque (
      id_estoque      SERIAL PRIMARY KEY,
      id_produto      INT REFERENCES produto(id_produto),
      id_loja         INT REFERENCES loja(id_loja),
      quantidade_atual   INT,
      quantidade_minima  INT,
      quantidade_maxima  INT,
      UNIQUE (id_produto,id_loja)
    );
    -- Promoções
    CREATE TABLE IF NOT EXISTS promocao (
      id_promocao          SERIAL PRIMARY KEY,
      nome_promocao        VARCHAR(100) NOT NULL,
      descricao            TEXT,
      data_inicio          DATE,
      data_fim             DATE,
      percentual_desconto  DECIMAL(5,2),
      ativa                BOOLEAN DEFAULT TRUE
    );
    CREATE TABLE IF NOT EXISTS produto_promocao (
      id_promocao INT REFERENCES promocao(id_promocao),
      id_produto  INT REFERENCES produto(id_produto),
      preco_promocional DECIMAL(10,2),
      PRIMARY KEY (id_promocao,id_produto)
    );
    -- Vendas & DW
    CREATE TABLE IF NOT EXISTS venda (
      id_venda     SERIAL PRIMARY KEY,
      id_produto   INT REFERENCES produto(id_produto),
      quantidade   INT NOT NULL,
      valor_total  DECIMAL(12,2),
      data_venda   TIMESTAMP NOT NULL
    );
    CREATE TABLE IF NOT EXISTS dim_tempo (
      data       DATE PRIMARY KEY,
      ano        INT, mes INT, dia INT, trimestre INT
    );
    CREATE TABLE IF NOT EXISTS fato_venda (
      id_fato     SERIAL PRIMARY KEY,
      data        DATE REFERENCES dim_tempo(data),
      produto_id  INT REFERENCES produto(id_produto),
      quantidade  INT,
      valor_total DECIMAL(12,2)
    );
    """
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    conn.close()

# ——— CRUD Categoria ———
def cadastrar_categoria(nome, descricao=None):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categoria(nome_categoria,descricao) VALUES(%s,%s) RETURNING id_categoria;",
                (nome,descricao)
            )
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_categorias():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM categoria ORDER BY id_categoria;")
        rows = cur.fetchall()
    conn.close()
    return rows

# ——— CRUD Produto ———
def cadastrar_produto(p):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO produto
                  (codigo_produto,nome_produto,descricao,id_categoria,
                   marca,preco_atual,unidade_medida,ativo)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                  RETURNING id_produto;""",
                (p.codigo_produto,p.nome_produto,p.descricao,
                 p.id_categoria,p.marca,p.preco_atual,
                 p.unidade_medida,p.ativo)
            )
            pid = cur.fetchone()[0]
    conn.close()
    return pid

def listar_produtos():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM produto ORDER BY id_produto;")
        rows = cur.fetchall()
    conn.close()
    return rows

# ——— CRUD Cliente ———
def cadastrar_cliente(c):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO cliente
                  (cpf,nome,email,telefone,endereco,cidade,estado,cep,ativo)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  RETURNING id_cliente;""",
                (c.cpf,c.nome,c.email,c.telefone,
                 c.endereco,c.cidade,c.estado,c.cep,c.ativo)
            )
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_clientes():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM cliente ORDER BY id_cliente;")
        rows = cur.fetchall()
    conn.close()
    return rows

# ——— CRUD Loja ———
def cadastrar_loja(l):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO loja
                  (codigo_loja,nome_loja,endereco,cidade,estado,cep,telefone,gerente,ativa)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  RETURNING id_loja;""",
                (l.codigo_loja,l.nome_loja,l.endereco,
                 l.cidade,l.estado,l.cep,l.telefone,l.gerente,l.ativa)
            )
            lid = cur.fetchone()[0]
    conn.close()
    return lid

def listar_lojas():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM loja ORDER BY id_loja;")
        rows = cur.fetchall()
    conn.close()
    return rows

# ——— CRUD Funcionário ———
def cadastrar_funcionario(f):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO funcionario
                  (codigo_funcionario,nome,cargo,id_loja,salario,ativo)
                  VALUES(%s,%s,%s,%s,%s,%s)
                  RETURNING id_funcionario;""",
                (f.codigo_funcionario,f.nome,f.cargo,f.id_loja,f.salario,f.ativo)
            )
            fid = cur.fetchone()[0]
    conn.close()
    return fid

def listar_funcionarios():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM funcionario ORDER BY id_funcionario;")
        rows = cur.fetchall()
    conn.close()
    return rows

# ——— CRUD Fornecedor ———
def cadastrar_fornecedor(f):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO fornecedor
                  (cnpj,razao_social,nome_fantasia,telefone,email,endereco,cidade,estado,ativo)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  RETURNING id_fornecedor;""",
                (f.cnpj,f.razao_social,f.nome_fantasia,
                 f.telefone,f.email,f.endereco,f.cidade,f.estado,f.ativo)
            )
            fid = cur.fetchone()[0]
    conn.close()
    return fid

def listar_fornecedores():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM fornecedor ORDER BY id_fornecedor;")
        rows = cur.fetchall()
    conn.close()
    return rows

# ——— CRUD Compra & ItemCompra ———
def cadastrar_compra(c: dict):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO compra
                  (numero_compra,id_fornecedor,id_loja,data_compra,valor_total,status_compra)
                  VALUES(%s,%s,%s,%s,%s,%s)
                  RETURNING id_compra;""",
                (c['numero_compra'],c['id_fornecedor'],c['id_loja'],
                 c['data_compra'],c['valor_total'],c['status_compra'])
            )
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_compras():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM compra ORDER BY id_compra;")
        return cur.fetchall()

def cadastrar_item_compra(i: dict):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            valor = i.get('valor_total', i['quantidade']*i['preco_unitario'])
            cur.execute(
                """INSERT INTO item_compra
                  (id_compra,id_produto,quantidade,preco_unitario,valor_total)
                  VALUES(%s,%s,%s,%s,%s) RETURNING id_item;""",
                (i['id_compra'],i['id_produto'],i['quantidade'],
                 i['preco_unitario'],valor)
            )
            return cur.fetchone()[0]

def listar_itens_compra():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM item_compra ORDER BY id_item;")
        return cur.fetchall()

# ——— CRUD Estoque ———
def atualizar_estoque(e: dict):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO estoque
                  (id_produto,id_loja,quantidade_atual,quantidade_minima,quantidade_maxima)
                  VALUES(%s,%s,%s,%s,%s)
                  ON CONFLICT(id_produto,id_loja) DO UPDATE
                  SET quantidade_atual=EXCLUDED.quantidade_atual,
                      quantidade_minima=EXCLUDED.quantidade_minima,
                      quantidade_maxima=EXCLUDED.quantidade_maxima;""",
                (e['id_produto'],e['id_loja'],
                 e['quantidade_atual'],e['quantidade_minima'],e['quantidade_maxima'])
            )
    conn.close()
    return True

def listar_estoque():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM estoque ORDER BY id_estoque;")
        return cur.fetchall()

# ——— CRUD Venda & DW ———
def registrar_venda(id_produto, quantidade, valor_total, data_venda):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO venda(id_produto,quantidade,valor_total,data_venda) VALUES(%s,%s,%s,%s);",
                (id_produto,quantidade,valor_total,data_venda)
            )
            cur.execute(
                """INSERT INTO dim_tempo(data,ano,mes,dia,trimestre)
                   VALUES(%s,EXTRACT(YEAR FROM %s::date),
                             EXTRACT(MONTH FROM %s::date),
                             EXTRACT(DAY FROM %s::date),
                             EXTRACT(QUARTER FROM %s::date))
                   ON CONFLICT(data) DO NOTHING;""",
                (data_venda,)*5
            )
            cur.execute(
                "INSERT INTO fato_venda(data,produto_id,quantidade,valor_total) VALUES(%s,%s,%s,%s);",
                (data_venda,id_produto,quantidade,valor_total)
            )
    conn.close()

def fetch_vendas_por_trimestre():
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """SELECT ano,trimestre,SUM(valor_total) AS total
               FROM fato_venda JOIN dim_tempo USING(data)
               GROUP BY ano,trimestre
               ORDER BY ano,trimestre;"""
        )
        return cur.fetchall()
