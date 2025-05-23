-- =================================
-- STAR SCHEMA (DW)
-- =================================

-- 1) Dimensão Tempo
CREATE TABLE IF NOT EXISTS dim_tempo (
  id_tempo   SERIAL    PRIMARY KEY,
  data       DATE      UNIQUE,
  ano        INT,
  mes        INT,
  dia        INT,
  trimestre  INT
);

-- 2) Dimensão Produto
-- (supondo que produto já existe no operacional)
CREATE TABLE IF NOT EXISTS dim_produto (
  id_produto   INT      PRIMARY KEY,
  nome_produto TEXT,
  marca        TEXT,
  id_categoria INT
);

-- Popula dim_produto a partir de produto
INSERT INTO dim_produto (id_produto, nome_produto, marca, id_categoria)
SELECT id_produto, nome_produto, marca, id_categoria
  FROM produto
ON CONFLICT (id_produto) DO NOTHING;

-- 3) Dimensão Loja
CREATE TABLE IF NOT EXISTS dim_loja (
  id_loja   INT      PRIMARY KEY,
  nome_loja TEXT,
  cidade    TEXT,
  estado    TEXT
);

-- Popula dim_loja a partir de loja
INSERT INTO dim_loja (id_loja, nome_loja, cidade, estado)
SELECT id_loja, nome_loja, cidade, estado
  FROM loja
ON CONFLICT (id_loja) DO NOTHING;

-- 4) Fato Vendas
CREATE TABLE IF NOT EXISTS fato_venda (
  id_fato     SERIAL        PRIMARY KEY,
  id_tempo    INT           REFERENCES dim_tempo(id_tempo),
  id_produto  INT           REFERENCES dim_produto(id_produto),
  id_loja     INT           REFERENCES dim_loja(id_loja),
  quantidade  INT,
  valor_total NUMERIC(12,2)
);