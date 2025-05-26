# database/postgres.py
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
    -- Vendas & DW simplificado
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

# Categoria
def cadastrar_categoria(nome, descricao=None):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categoria (nome_categoria, descricao) VALUES (%s,%s) RETURNING id_categoria;",
                (nome, descricao)
            )
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_categorias():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM categoria ORDER BY id_categoria;")
            rows = cur.fetchall()
    conn.close()
    return rows

# Produto
def cadastrar_produto(p):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO produto
                  (codigo_produto,nome_produto,descricao,id_categoria,
                   marca,preco_atual,unidade_medida,ativo)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id_produto;
            """, (
                p.codigo_produto, p.nome_produto, p.descricao,
                p.id_categoria, p.marca, p.preco_atual,
                p.unidade_medida, p.ativo
            ))
            pid = cur.fetchone()[0]
    conn.close()
    return pid

def listar_produtos():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM produto ORDER BY id_produto;")
            rows = cur.fetchall()
    conn.close()
    return rows

# Cliente
def cadastrar_cliente(c):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cliente
                  (cpf,nome,email,telefone,endereco,cidade,estado,cep,ativo)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id_cliente;
            """, (
                c.cpf, c.nome, c.email, c.telefone,
                c.endereco, c.cidade, c.estado, c.cep, c.ativo
            ))
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_clientes():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM cliente ORDER BY id_cliente;")
            rows = cur.fetchall()
    conn.close()
    return rows

# Loja
def cadastrar_loja(l):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO loja
                  (codigo_loja,nome_loja,endereco,cidade,estado,cep,telefone,gerente,ativa)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id_loja;
            """, (
                l.codigo_loja, l.nome_loja, l.endereco,
                l.cidade, l.estado, l.cep,
                l.telefone, l.gerente, l.ativa
            ))
            lid = cur.fetchone()[0]
    conn.close()
    return lid

def listar_lojas():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM loja ORDER BY id_loja;")
            rows = cur.fetchall()
    conn.close()
    return rows

# Vendas & DW
def registrar_venda(id_produto, quantidade, valor_total, data_venda):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO venda (id_produto,quantidade,valor_total,data_venda) VALUES (%s,%s,%s,%s);",
                (id_produto, quantidade, valor_total, data_venda)
            )
            cur.execute("""
                INSERT INTO dim_tempo (data,ano,mes,dia,trimestre)
                VALUES (
                  %s,
                  EXTRACT(YEAR   FROM %s::date),
                  EXTRACT(MONTH  FROM %s::date),
                  EXTRACT(DAY    FROM %s::date),
                  EXTRACT(QUARTER FROM %s::date)
                ) ON CONFLICT (data) DO NOTHING;
            """, (data_venda,)*5)
            cur.execute(
                "INSERT INTO fato_venda (data,produto_id,quantidade,valor_total) VALUES (%s,%s,%s,%s);",
                (data_venda, id_produto, quantidade, valor_total)
            )
    conn.close()

def fetch_vendas_por_trimestre():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT ano,trimestre,SUM(valor_total) AS total
                  FROM fato_venda JOIN dim_tempo USING(data)
                 GROUP BY ano,trimestre
                 ORDER BY ano,trimestre;
            """)
            rows = cur.fetchall()
    conn.close()
    return rows
