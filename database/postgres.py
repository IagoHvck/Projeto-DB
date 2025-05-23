# database/postgres.py
import psycopg2
from psycopg2.extras import RealDictCursor
from config import POSTGRES

def conectar():
    return psycopg2.connect(**POSTGRES)

def criar_tabelas():
    sql = """
    -- Tabela de produtos (objeto-relacional)
    CREATE TABLE IF NOT EXISTS produto (
      id SERIAL PRIMARY KEY,
      nome VARCHAR(100) NOT NULL,
      categoria VARCHAR(50),
      marca VARCHAR(50),
      preco NUMERIC(10,2),
      estoque INT
    );

    -- Tabela de vendas operacionais
    CREATE TABLE IF NOT EXISTS venda (
      id SERIAL PRIMARY KEY,
      produto_id INT REFERENCES produto(id),
      quantidade INT NOT NULL,
      valor_total NUMERIC(12,2),
      data_venda DATE NOT NULL
    );

    -- Dimensão tempo (DW simplificado)
    CREATE TABLE IF NOT EXISTS dim_tempo (
      data DATE PRIMARY KEY,
      ano INT, mes INT, dia INT, trimestre INT
    );

    -- Fato vendas (DW simplificado)
    CREATE TABLE IF NOT EXISTS fato_venda (
      id SERIAL PRIMARY KEY,
      data DATE REFERENCES dim_tempo(data),
      produto_id INT,
      quantidade INT,
      valor_total NUMERIC(12,2)
    );
    """
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    conn.close()

def inserir_produto(prod):
    conn = conectar()
    sql = """
      INSERT INTO produto (nome,categoria,marca,preco,estoque)
      VALUES (%s,%s,%s,%s,%s) RETURNING id;
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (prod.nome, prod.categoria, prod.marca, prod.preco, prod.estoque))
            pid = cur.fetchone()[0]
    conn.close()
    return pid

def registrar_venda(pid, qtd, total, data):
    """
    pid   : int       — id do produto
    qtd   : int       — quantidade vendida
    total : float     — valor total da venda
    data  : datetime.date — data da venda
    """
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO venda
                  (produto_id, quantidade, valor_total, data_venda)
                VALUES (%s, %s, %s, %s)
                """,
                (pid, qtd, total, data),
            )
            cur.execute(
                """
                INSERT INTO dim_tempo (data, ano, mes, dia, trimestre)
                VALUES (
                  %s,
                  EXTRACT(YEAR   FROM %s::date),
                  EXTRACT(MONTH  FROM %s::date),
                  EXTRACT(DAY    FROM %s::date),
                  EXTRACT(QUARTER FROM %s::date)
                )
                ON CONFLICT (data) DO NOTHING
                """,
                (data, data, data, data, data),
            )
            cur.execute(
                """
                INSERT INTO fato_venda (data, produto_id, quantidade, valor_total)
                VALUES (%s, %s, %s, %s)
                """,
                (data, pid, qtd, total),
            )
    conn.close()


def fetch_vendas_por_trimestre():
    conn = conectar()
    sql = """
      SELECT ano, trimestre, SUM(valor_total) AS total
      FROM fato_venda
      JOIN dim_tempo USING(data)
      GROUP BY ano, trimestre
      ORDER BY ano, trimestre;
    """
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    conn.close()
    return rows
