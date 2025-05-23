from database_pg import fetch_all

def vendas_por_trimestre():
    sql = """
      SELECT t.ano, t.trimestre, SUM(f.valor_total) AS total
      FROM fato_venda f
      JOIN dim_tempo t ON t.id_tempo = f.id_tempo
      GROUP BY t.ano, t.trimestre
      ORDER BY t.ano, t.trimestre;
    """
    return fetch_all(sql)

def comentarios_do_produto(produto_id):
    from database_mongo import find_comments
    return find_comments(produto_id)
