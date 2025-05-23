import csv
from database_pg import exec_script
from database_mongo import insert_comment

def cria_bancos():
  exec_script("database/schema_operacional.sql")
  print("Operacional criado.")
  exec_script("database/schema_dw.sql")
  print("DW criado.")

def popula_operacional():
    # aqui você carrega CSVs de produtos, vendas, itens…
    pass

def popula_dw():
    # Popular dim_tempo a partir de venda.data_venda
    from database_pg import fetch_all, _engine
    tempos = fetch_all("SELECT DISTINCT DATE(data_venda) AS dt FROM venda;")
    with _engine.begin() as conn:
        for row in tempos:
            dt = row["dt"]
            conn.execute(text("""
              INSERT INTO dim_tempo (data, ano, mes, dia, trimestre)
              VALUES (:d, EXTRACT(YEAR FROM :d), EXTRACT(MONTH FROM :d),
                      EXTRACT(DAY FROM :d),
                      EXTRACT(QUARTER FROM :d))
              ON CONFLICT (data) DO NOTHING;
            """), {"d": dt})

    # Popular fato_venda
    conn = _engine.begin()
    conn.execute(text("""
      INSERT INTO fato_venda (id_tempo,id_produto,id_loja,quantidade,valor_total)
      SELECT 
        (SELECT id_tempo FROM dim_tempo WHERE data = DATE(v.data_venda)),
        iv.id_produto, v.id_loja, iv.quantidade, iv.valor_total
      FROM venda v JOIN item_venda iv ON iv.id_venda = v.id_venda;
    """))

def popula_nosql():
    # Exemplo de comentário:
    insert_comment({
      "produto_id": 1,
      "cliente_id": 42,
      "comentario": "Adorei!",
      "data": "2025-05-01T10:00:00"
    })
