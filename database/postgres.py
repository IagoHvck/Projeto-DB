# database/postgres.py
import psycopg2
from psycopg2.extras import RealDictCursor
from config import POSTGRES

def conectar():
    return psycopg2.connect(**POSTGRES)

def criar_tabelas():
    sql = """
    -- Tabelas operacionais básicas

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

    -- Vendas
    CREATE TABLE IF NOT EXISTS venda (
        id_venda       SERIAL PRIMARY KEY,
        numero_venda   VARCHAR(20) UNIQUE NOT NULL,
        id_cliente     INT REFERENCES cliente(id_cliente),
        id_loja        INT REFERENCES loja(id_loja),
        id_funcionario INT REFERENCES funcionario(id_funcionario),
        data_venda     TIMESTAMP NOT NULL,
        valor_total    DECIMAL(10,2),
        desconto_total DECIMAL(10,2),
        forma_pagamento VARCHAR(30),
        status_venda    VARCHAR(20)
    );

    -- Itens de Venda
    CREATE TABLE IF NOT EXISTS item_venda (
        id_item        SERIAL PRIMARY KEY,
        id_venda       INT REFERENCES venda(id_venda),
        id_produto     INT REFERENCES produto(id_produto),
        quantidade     INT,
        preco_unitario DECIMAL(10,2),
        desconto       DECIMAL(10,2),
        valor_total    DECIMAL(10,2)
    );

    -- Fornecedores
    CREATE TABLE IF NOT EXISTS fornecedor (
        id_fornecedor SERIAL PRIMARY KEY,
        cnpj          VARCHAR(14) UNIQUE NOT NULL,
        razao_social  VARCHAR(100) NOT NULL,
        nome_fantasia VARCHAR(100),
        telefone      VARCHAR(20),
        email         VARCHAR(100),
        endereco      VARCHAR(200),
        cidade        VARCHAR(50),
        estado        CHAR(2),
        ativo         BOOLEAN DEFAULT TRUE
    );

    -- Produto x Fornecedor
    CREATE TABLE IF NOT EXISTS produto_fornecedor (
        id_produto    INT REFERENCES produto(id_produto),
        id_fornecedor INT REFERENCES fornecedor(id_fornecedor),
        preco_compra  DECIMAL(10,2),
        prazo_entrega INT,
        PRIMARY KEY (id_produto, id_fornecedor)
    );

    -- Estoque
    CREATE TABLE IF NOT EXISTS estoque (
        id_estoque       SERIAL PRIMARY KEY,
        id_produto       INT REFERENCES produto(id_produto),
        id_loja          INT REFERENCES loja(id_loja),
        quantidade_atual INT,
        quantidade_minima INT,
        quantidade_maxima INT,
        UNIQUE (id_produto, id_loja)
    );

    -- Compras
    CREATE TABLE IF NOT EXISTS compra (
        id_compra    SERIAL PRIMARY KEY,
        numero_compra VARCHAR(20) UNIQUE NOT NULL,
        id_fornecedor INT REFERENCES fornecedor(id_fornecedor),
        id_loja       INT REFERENCES loja(id_loja),
        data_compra   TIMESTAMP,
        valor_total   DECIMAL(10,2),
        status_compra VARCHAR(20)
    );

    -- Itens de Compra
    CREATE TABLE IF NOT EXISTS item_compra (
        id_item        SERIAL PRIMARY KEY,
        id_compra      INT REFERENCES compra(id_compra),
        id_produto     INT REFERENCES produto(id_produto),
        quantidade     INT,
        preco_unitario DECIMAL(10,2),
        valor_total    DECIMAL(10,2)
    );

    -- Avaliações
    CREATE TABLE IF NOT EXISTS avaliacao (
        id_avaliacao  SERIAL PRIMARY KEY,
        id_produto    INT REFERENCES produto(id_produto),
        id_cliente    INT REFERENCES cliente(id_cliente),
        data_avaliacao TIMESTAMP,
        nota          INT CHECK (nota BETWEEN 1 AND 5),
        comentario    TEXT
    );

    -- Promoções
    CREATE TABLE IF NOT EXISTS promocao (
        id_promocao       SERIAL PRIMARY KEY,
        nome_promocao     VARCHAR(100) NOT NULL,
        descricao         TEXT,
        data_inicio       DATE,
        data_fim          DATE,
        percentual_desconto DECIMAL(5,2),
        ativa             BOOLEAN DEFAULT TRUE
    );

    -- Produto em Promoção
    CREATE TABLE IF NOT EXISTS produto_promocao (
        id_promocao INT REFERENCES promocao(id_promocao),
        id_produto  INT REFERENCES produto(id_produto),
        preco_promocional DECIMAL(10,2),
        PRIMARY KEY (id_promocao, id_produto)
    );

    -- DW simplificado
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

    -- Índices
    CREATE INDEX IF NOT EXISTS idx_venda_data       ON venda(data_venda);
    CREATE INDEX IF NOT EXISTS idx_venda_cliente    ON venda(id_cliente);
    CREATE INDEX IF NOT EXISTS idx_produto_categoria ON produto(id_categoria);
    CREATE INDEX IF NOT EXISTS idx_avaliacao_produto ON avaliacao(id_produto);
    CREATE INDEX IF NOT EXISTS idx_estoque_produto  ON estoque(id_produto);
    """
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    conn.close()


# --- CRUD Categoria ---
def cadastrar_categoria(nome, descricao=None):
    conn = conectar()
    sql = """
      INSERT INTO categoria (nome_categoria, descricao)
      VALUES (%s,%s) RETURNING id_categoria;
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (nome, descricao))
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_categorias():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM categoria ORDER BY id_categoria")
            data = cur.fetchall()
    conn.close()
    return data

# --- CRUD Produto ---
def cadastrar_produto(p):
    conn = conectar()
    sql = """
      INSERT INTO produto
        (codigo_produto,nome_produto,descricao,
         id_categoria,marca,preco_atual,unidade_medida,ativo)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
      RETURNING id_produto;
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                p.codigo_produto,
                p.nome_produto,
                p.descricao,
                p.id_categoria,
                p.marca,
                p.preco_atual,
                p.unidade_medida,
                p.ativo
            ))
            pid = cur.fetchone()[0]
    conn.close()
    return pid

def listar_produtos():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM produto ORDER BY id_produto")
            data = cur.fetchall()
    conn.close()
    return data

# --- Exemplo simples para Cliente ---
def cadastrar_cliente(c):
    conn = conectar()
    sql = """
      INSERT INTO cliente (cpf, nome, email, telefone, endereco, cidade, estado, cep, ativo)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
      RETURNING id_cliente;
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                c.cpf, c.nome, c.email, c.telefone, c.endereco,
                c.cidade, c.estado, c.cep, c.ativo
            ))
            cid = cur.fetchone()[0]
    conn.close()
    return cid

def listar_clientes():
    conn = conectar()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM cliente ORDER BY id_cliente")
            data = cur.fetchall()
    conn.close()
    return data

# Adicione aqui funcoes semelhantes para loja, funcionario, fornecedor, etc. conforme sua necessidade.

# --- VENDAS ---
def registrar_venda(id_cliente, id_loja, id_funcionario, data_venda,
                    valor_total, desconto_total=0, forma_pag='-', status='Finalizada'):
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO venda
                  (numero_venda, id_cliente,id_loja,id_funcionario,
                   data_venda,valor_total,desconto_total,forma_pagamento,status_venda)
                VALUES
                  (CONCAT('VD',TO_CHAR(NOW(),'YYYYMMDDHH24MISS')), %s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (id_cliente, id_loja, id_funcionario, data_venda,
                 valor_total, desconto_total, forma_pag, status)
            )
    conn.close()
