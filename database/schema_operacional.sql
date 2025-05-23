-- =================================
-- OPERACIONAL
-- =================================

-- 1) Tabela de produtos
CREATE TABLE IF NOT EXISTS produto (
    id_produto     SERIAL PRIMARY KEY,
    codigo_produto VARCHAR(20) UNIQUE NOT NULL,
    nome_produto   VARCHAR(100) NOT NULL,
    descricao      TEXT,
    id_categoria   INT,
    marca          VARCHAR(50),
    preco_atual    NUMERIC(10,2) NOT NULL DEFAULT 0,
    unidade_medida VARCHAR(20),
    ativo          BOOLEAN       NOT NULL DEFAULT TRUE
    -- (você pode adicionar um FK para categoria caso já exista,
    --  ex: , FOREIGN KEY(id_categoria) REFERENCES categoria(id_categoria))
);

-- 2) Tabela de vendas
CREATE TABLE IF NOT EXISTS venda (
    id_venda       SERIAL PRIMARY KEY,
    numero_venda   VARCHAR(20) UNIQUE NOT NULL,
    id_cliente     INT,
    id_loja        INT,
    id_funcionario INT,
    data_venda     TIMESTAMP    NOT NULL DEFAULT NOW(),
    valor_total    NUMERIC(12,2) NOT NULL DEFAULT 0,
    desconto_total NUMERIC(12,2) NOT NULL DEFAULT 0,
    forma_pagamento VARCHAR(30),
    status_venda    VARCHAR(20)  NOT NULL DEFAULT 'ABERTA'
    -- , FOREIGN KEY(id_cliente) REFERENCES cliente(id_cliente)
    -- , FOREIGN KEY(id_loja) REFERENCES loja(id_loja)
    -- , FOREIGN KEY(id_funcionario) REFERENCES funcionario(id_funcionario)
);

-- 3) Tabela de itens de venda
CREATE TABLE IF NOT EXISTS item_venda (
    id_item        SERIAL PRIMARY KEY,
    id_venda       INT    NOT NULL,
    id_produto     INT    NOT NULL,
    quantidade     INT    NOT NULL DEFAULT 1,
    preco_unitario NUMERIC(10,2) NOT NULL DEFAULT 0,
    desconto       NUMERIC(10,2) NOT NULL DEFAULT 0,
    valor_total    NUMERIC(12,2) NOT NULL,
    FOREIGN KEY(id_venda)   REFERENCES venda(id_venda) ON DELETE CASCADE,
    FOREIGN KEY(id_produto) REFERENCES produto(id_produto) ON DELETE RESTRICT
);

-- Índices auxiliares para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_venda_data       ON venda(data_venda);
CREATE INDEX IF NOT EXISTS idx_item_venda_prod   ON item_venda(id_produto);
