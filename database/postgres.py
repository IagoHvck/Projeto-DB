import psycopg2
from config import POSTGRES

def conectar_postgres():
    conn = psycopg2.connect(**POSTGRES)
    return conn

def criar_tabelas():
    conn = conectar_postgres()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_produto (
        id SERIAL PRIMARY KEY,
        nome VARCHAR,
        categoria VARCHAR,
        marca VARCHAR
    );

    CREATE TABLE IF NOT EXISTS fato_vendas (
        id SERIAL PRIMARY KEY,
        id_produto INT REFERENCES dim_produto(id),
        quantidade INT,
        valor_total NUMERIC
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
