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
from yullop import print_zodb_tree, print_zodb_tables, print_zodb_tree_completo
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
from database.test import test_integracao

console = Console()

# main.py (ou onde estiver o seu popular())
from database.postgres import conectar
from database.migrator import migrar_tudo_para_zodb

def popular():
    from database.postgres import conectar
    inserts = [
        # 1) Categorias
        ("""
         INSERT INTO categoria (nome_categoria, descricao)
         VALUES (%s, %s)
         ON CONFLICT DO NOTHING;
        """, [
             ('Eletrônicos', 'Produtos eletrônicos, tecnologia e informática'),
             ('Alimentos e Bebidas', 'Produtos alimentícios, bebidas e snacks'),
             ('Vestuário', 'Roupas, calçados e acessórios'),
             ('Casa e Decoração', 'Móveis, decoração e utilidades domésticas'),
             ('Esportes e Lazer', 'Produtos esportivos e equipamentos de lazer'),
             ('Beleza e Cuidados', 'Cosméticos, perfumaria e cuidados pessoais'),
             ('Livros e Papelaria', 'Livros, material escolar e escritório'),
             ('Brinquedos', 'Brinquedos e jogos infantis'),
        ]),

        # 2) Lojas
        ("""
         INSERT INTO loja
           (codigo_loja, nome_loja, endereco, cidade, estado, cep, telefone, gerente)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
         ON CONFLICT (codigo_loja) DO NOTHING;
        """, [
            ('LJ001', 'Loja Shopping Center', 'Av. Paulista, 1500', 'São Paulo', 'SP', '01310100', '11-3456-7890', 'Carlos Silva'),
            ('LJ002', 'Loja Barra Shopping', 'Av. das Américas, 4666', 'Rio de Janeiro', 'RJ', '22640102', '21-2431-8900', 'Ana Santos'),
            ('LJ003', 'Loja BH Shopping', 'Rod. BR-356, 3049', 'Belo Horizonte', 'MG', '31150900', '31-3456-7890', 'Pedro Oliveira'),
            ('LJ004', 'Loja Recife Shopping', 'Av. Agamenon Magalhães, 1000', 'Recife', 'PE', '52070000', '81-3456-7890', 'Maria Costa'),
            ('LJ005', 'Loja Salvador Shopping', 'Av. Tancredo Neves, 2915', 'Salvador', 'BA', '41820021', '71-3456-7890', 'João Pereira'),
            ('LJ006', 'Loja Porto Alegre', 'Av. Diário de Notícias, 300', 'Porto Alegre', 'RS', '90810000', '51-3456-7890', 'Paula Lima'),
            ('LJ007', 'Loja Brasília Shopping', 'SCN Q 6 L 2', 'Brasília', 'DF', '70716900', '61-3456-7890', 'Roberto Alves'),
            ('LJ008', 'Loja Curitiba Shopping', 'Av. das Torres, 1700', 'Curitiba', 'PR', '82840730', '41-3456-7890', 'Juliana Martins'),
        ]),

        # 3) Produtos
        ("""
         INSERT INTO produto
           (codigo_produto,nome_produto,descricao,id_categoria,marca,preco_atual,unidade_medida,ativo)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
         ON CONFLICT (codigo_produto) DO NOTHING;
        """, [
            ('ELET001', 'Smartphone Galaxy S22', 'Smartphone Samsung Galaxy S22 128GB', 1, 'Samsung', 3499.00, 'UN', True),
            ('ELET002', 'Notebook Dell Inspiron 15', 'Notebook Dell i5 8GB RAM 512GB SSD', 1, 'Dell', 2899.00, 'UN', True),
            ('ELET003', 'TV Smart 50" 4K', 'Smart TV LG 50 polegadas 4K', 1, 'LG', 2199.00, 'UN', True),
            ('ELET004', 'Fone Bluetooth', 'Fone de ouvido bluetooth JBL', 1, 'JBL', 249.90, 'UN', True),
            ('ELET005', 'Mouse Gamer', 'Mouse gamer RGB Logitech', 1, 'Logitech', 199.90, 'UN', True),

            ('ALIM001', 'Café Premium 500g', 'Café torrado e moído premium', 2, 'Melitta', 24.90, 'PCT', True),
            ('ALIM002', 'Chocolate ao Leite 200g', 'Chocolate ao leite Nestlé', 2, 'Nestlé', 8.90, 'UN', True),
            ('ALIM003', 'Água Mineral 1,5L', 'Água mineral sem gás', 2, 'Crystal', 2.90, 'UN', True),
            ('ALIM004', 'Biscoito Integral', 'Biscoito integral multigrãos', 2, 'Vitarella', 4.50, 'PCT', True),
            ('ALIM005', 'Suco Natural 1L', 'Suco de laranja natural', 2, 'Del Valle', 7.90, 'UN', True),

            ('VEST001', 'Camisa Polo Masculina', 'Camisa polo algodão masculina', 3, 'Lacoste', 189.90, 'UN', True),
            ('VEST002', 'Calça Jeans Feminina', 'Calça jeans feminina skinny', 3, 'Levi\'s', 259.90, 'UN', True),
            ('VEST003', 'Tênis Running', 'Tênis para corrida unissex', 3, 'Nike', 399.90, 'PAR', True),
            ('VEST004', 'Vestido Casual', 'Vestido casual feminino', 3, 'Renner', 119.90, 'UN', True),
            ('VEST005', 'Mochila Escolar', 'Mochila escolar resistente', 3, 'Samsonite', 149.90, 'UN', True),

            ('CASA001', 'Jogo de Panelas 5 peças', 'Jogo de panelas antiaderente', 4, 'Tramontina', 299.90, 'JG', True),
            ('CASA002', 'Edredom Casal', 'Edredom casal 100% algodão', 4, 'Santista', 189.90, 'UN', True),
            ('CASA003', 'Conjunto de Toalhas', 'Kit 4 toalhas de banho', 4, 'Karsten', 99.90, 'KIT', True),
            ('CASA004', 'Luminária de Mesa', 'Luminária LED para mesa', 4, 'Philips', 89.90, 'UN', True),
            ('CASA005', 'Organizador Multiuso', 'Organizador plástico com divisórias', 4, 'Ordene', 39.90, 'UN', True),

            ('ESPO001', 'Bola de Futebol', 'Bola de futebol oficial', 5, 'Adidas', 129.90, 'UN', True),
            ('ESPO002', 'Kit Halteres 10kg', 'Par de halteres ajustáveis', 5, 'Kikos', 199.90, 'KIT', True),
            ('ESPO003', 'Tapete Yoga', 'Tapete para yoga antiderrapante', 5, 'Acte Sports', 79.90, 'UN', True),
            ('ESPO004', 'Bicicleta Aro 29', 'Mountain bike aro 29', 5, 'Caloi', 1499.00, 'UN', True),
            ('ESPO005', 'Corda de Pular', 'Corda de pular profissional', 5, 'Speedo', 39.90, 'UN', True),

            ('BELZ001', 'Shampoo 400ml', 'Shampoo hidratante', 6, 'Pantene', 18.90, 'UN', True),
            ('BELZ002', 'Creme Hidratante 200ml', 'Creme hidratante corporal', 6, 'Nivea', 24.90, 'UN', True),
            ('BELZ003', 'Perfume Masculino 100ml', 'Perfume masculino amadeirado', 6, 'Boticário', 189.90, 'UN', True),
            ('BELZ004', 'Base Líquida', 'Base líquida cobertura média', 6, 'MAC', 249.90, 'UN', True),
            ('BELZ005', 'Kit Maquiagem', 'Kit maquiagem completo', 6, 'Ruby Rose', 89.90, 'KIT', True),

            ('LIVR001', 'Livro Best Seller', 'Romance contemporâneo', 7, 'Intrínseca', 49.90, 'UN', True),
            ('LIVR002', 'Caderno Universitário', 'Caderno 200 folhas', 7, 'Tilibra', 24.90, 'UN', True),
            ('LIVR003', 'Kit Canetas Coloridas', 'Kit 12 canetas coloridas', 7, 'BIC', 19.90, 'KIT', True),
            ('LIVR004', 'Agenda 2024', 'Agenda executiva 2024', 7, 'Foroni', 34.90, 'UN', True),
            ('LIVR005', 'Calculadora Científica', 'Calculadora científica completa', 7, 'Casio', 89.90, 'UN', True),

            ('BRIN001', 'Lego Classic 500 peças', 'Kit Lego construção classic', 8, 'Lego', 299.90, 'CX', True),
            ('BRIN002', 'Boneca Fashion', 'Boneca fashion com acessórios', 8, 'Mattel', 149.90, 'UN', True),
            ('BRIN003', 'Quebra-cabeça 1000 peças', 'Quebra-cabeça paisagem', 8, 'Grow', 59.90, 'CX', True),
            ('BRIN004', 'Carrinho Hot Wheels', 'Carrinho colecionável', 8, 'Hot Wheels', 12.90, 'UN', True),
            ('BRIN005', 'Jogo de Tabuleiro', 'Jogo War clássico', 8, 'Grow', 89.90, 'CX', True),
        ]),

        # 4) Funcionários
        ("""
         INSERT INTO funcionario
           (codigo_funcionario,nome,cargo,id_loja,salario,ativo)
         VALUES (%s,%s,%s,%s,%s,%s)
         ON CONFLICT (codigo_funcionario) DO NOTHING;
        """, [
            ('FUNC001','Carlos Silva','Gerente',1,8000.00,True),
            ('FUNC002','Mariana Rocha','Vendedor',1,2500.00,True),

            ('FUNC001', 'Carlos Silva', 'Gerente', 1, 8000.00,True),
            ('FUNC002', 'Mariana Rocha', 'Vendedor', 1, 2500.00,True),
            ('FUNC003', 'José Santos', 'Vendedor', 1, 2500.00,True),
            ('FUNC004', 'Laura Ferreira', 'Caixa', 1, 2200.00,True),

            ('FUNC005', 'Ana Santos', 'Gerente', 2, 8000.00,True),
            ('FUNC006', 'Bruno Costa', 'Vendedor', 2, 2500.00,True),
            ('FUNC007', 'Carla Almeida', 'Vendedor', 2, 2500.00,True),
            ('FUNC008', 'Diego Pereira', 'Caixa', 2, 2200.00,True),

            ('FUNC009', 'Pedro Oliveira', 'Gerente', 3, 8000.00,True),
            ('FUNC010', 'Fernanda Lima', 'Vendedor', 3, 2500.00,True),
            ('FUNC011', 'Ricardo Silva', 'Vendedor', 3, 2500.00,True),
            ('FUNC012', 'Tatiana Souza', 'Caixa', 3, 2200.00,True),

            ('FUNC013', 'Maria Costa', 'Gerente', 4, 8000.00,True),
            ('FUNC014', 'Anderson Melo', 'Vendedor', 4, 2500.00,True),
            ('FUNC015', 'Beatriz Nunes', 'Vendedor', 4, 2500.00,True),
            ('FUNC016', 'Cláudio Ribeiro', 'Caixa', 4, 2200.00,True),

            ('FUNC017', 'João Pereira', 'Gerente', 5, 8000.00,True),
            ('FUNC018', 'Sandra Matos', 'Vendedor', 5, 2500.00,True),
            ('FUNC019', 'Marcos Dias', 'Vendedor', 5, 2500.00,True),
            ('FUNC020', 'Elaine Barros', 'Caixa', 5, 2200.00,True),
        ]),

        # 5) Clientes
        ("""
         INSERT INTO cliente
           (cpf,nome,email,telefone,endereco,cidade,estado,cep,ativo)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
         ON CONFLICT (cpf) DO NOTHING;
        """, [
            ('12345678901', 'Paulo Henrique Silva', 'paulo.silva@email.com', '11-98765-4321', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234567',True),
            ('23456789012', 'Ana Maria Santos', 'ana.santos@email.com', '11-97654-3210', 'Av. Paulista, 456', 'São Paulo', 'SP', '01310100',True),
            ('34567890123', 'Roberto Carlos Oliveira', 'roberto.oliveira@email.com', '21-96543-2109', 'Rua Copacabana, 789', 'Rio de Janeiro', 'RJ', '22020050',True),
            ('45678901234', 'Juliana Costa Lima', 'juliana.lima@email.com', '31-95432-1098', 'Av. Afonso Pena, 321', 'Belo Horizonte', 'MG', '30130005',True),
            ('56789012345', 'Fernando Alves Costa', 'fernando.costa@email.com', '81-94321-0987', 'Av. Boa Viagem, 654', 'Recife', 'PE', '51020180',True),
            ('67890123456', 'Mariana Ferreira Souza', 'mariana.souza@email.com', '71-93210-9876', 'Av. Oceânica, 987', 'Salvador', 'BA', '40160060',True),
            ('78901234567', 'Alexandre Martins Silva', 'alexandre.silva@email.com', '51-92109-8765', 'Rua da Praia, 147', 'Porto Alegre', 'RS', '90020060',True),
            ('89012345678', 'Camila Rodrigues Santos', 'camila.santos@email.com', '61-91098-7654', 'SQS 308 Bloco C', 'Brasília', 'DF', '70355030',True),
            ('90123456789', 'Ricardo Pereira Lima', 'ricardo.lima@email.com', '41-90987-6543', 'Rua XV de Novembro, 258', 'Curitiba', 'PR', '80020310',True),
            ('01234567890', 'Patricia Almeida Costa', 'patricia.costa@email.com', '11-89876-5432', 'Alameda Santos, 369', 'São Paulo', 'SP', '01419002',True),
            ('11223344556', 'Bruno Carvalho Dias', 'bruno.dias@email.com', '21-88765-4321', 'Av. Rio Branco, 741', 'Rio de Janeiro', 'RJ', '20040008',True),
            ('22334455667', 'Letícia Nunes Oliveira', 'leticia.oliveira@email.com', '31-87654-3210', 'Rua da Bahia, 852', 'Belo Horizonte', 'MG', '30160011',True),
            ('33445566778', 'Carlos Eduardo Santos', 'carlos.santos@email.com', '81-86543-2109', 'Rua do Sol, 963', 'Recife', 'PE', '50030230',True),
            ('44556677889', 'Daniela Sousa Lima', 'daniela.lima@email.com', '71-85432-1098', 'Av. Sete de Setembro, 159', 'Salvador', 'BA', '40060500',True),
            ('55667788990', 'Marcelo Ferreira Costa', 'marcelo.costa@email.com', '51-84321-0987', 'Av. Ipiranga, 753', 'Porto Alegre', 'RS', '90160091',True),
        ]),

        # 6) Fornecedores
        ("""
         INSERT INTO fornecedor
           (cnpj,razao_social,nome_fantasia,telefone,email,endereco,cidade,estado,ativo)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
         ON CONFLICT (cnpj) DO NOTHING;
        """, [
            ('12345678000100', 'Samsung Eletrônicos do Brasil LTDA', 'Samsung Brasil', '11-5644-2000', 'contato@samsung.com.br', 'Av. Dr. Chucri Zaidan, 1240', 'São Paulo', 'SP',True),
            ('23456789000111', 'Dell Computadores do Brasil LTDA', 'Dell Brasil', '11-5503-5000', 'vendas@dell.com.br', 'Av. Industrial, 700', 'Eldorado do Sul', 'RS',True),
            ('34567890000122', 'Nestlé Brasil LTDA', 'Nestlé', '11-2199-2999', 'faleconosco@nestle.com.br', 'Av. Nações Unidas, 12495', 'São Paulo', 'SP',True),
            ('45678901000133', 'Nike do Brasil Com. e Part. LTDA', 'Nike Brasil', '11-5102-4400', 'atendimento@nike.com.br', 'Av. das Nações Unidas, 14261', 'São Paulo', 'SP',True),
            ('56789012000144', 'Tramontina S.A.', 'Tramontina', '54-3461-8200', 'sac@tramontina.com.br', 'Rod. RS-324 Km 2,5', 'Carlos Barbosa', 'RS',True),
            ('67890123000155', 'Procter & Gamble do Brasil S.A.', 'P&G Brasil', '11-3046-5800', 'atendimento@pg.com.br', 'Av. Brigadeiro Faria Lima, 3900', 'São Paulo', 'SP',True),
            ('78901234000166', 'Mattel do Brasil LTDA', 'Mattel', '11-5090-8500', 'sac@mattel.com.br', 'Av. Tamboré, 1400', 'Barueri', 'SP',True),
            ('89012345000177', 'Editora Intrínseca LTDA', 'Intrínseca', '21-2206-7400', 'contato@intrinseca.com.br', 'Rua Marquês de São Vicente, 99', 'Rio de Janeiro', 'RJ',True),
            ('90123456000188', 'JBL do Brasil', 'JBL', '11-3048-1700', 'suporte@jbl.com.br', 'Rua James Clerk Maxwell, 170', 'Campinas', 'SP',True),
            ('01234567000199', 'Melitta do Brasil', 'Melitta', '47-3801-5000', 'sac@melitta.com.br', 'Rua Dona Francisca, 8300', 'Joinville', 'SC',True),
        ]),

        # 7) Compras
        ("""
         INSERT INTO compra
           (numero_compra,id_fornecedor,id_loja,data_compra,valor_total,status_compra)
         VALUES (%s,%s,%s,%s,%s,%s)
         ON CONFLICT (numero_compra) DO NOTHING;
        """, [
            ('CP202401001', 1, 1, '2024-01-05 09:00:00', 28000.00, 'Recebida'),
            ('CP202401002', 2, 1, '2024-01-08 10:30:00', 11500.00, 'Recebida'),
            ('CP202401003', 3, 2, '2024-01-10 14:00:00', 1355.00, 'Recebida'),
            ('CP202401004', 4, 3, '2024-01-12 11:15:00', 6400.00, 'Recebida'),
            ('CP202401005', 5, 4, '2024-01-14 15:30:00', 2400.00, 'Recebida'),
            ('CP202401006', 6, 5, '2024-01-16 09:45:00', 850.00, 'Em Trânsito'),
            ('CP202401007', 7, 6, '2024-01-18 13:00:00', 3600.00, 'Recebida'),
            ('CP202401008', 8, 7, '2024-01-20 10:00:00', 390.00, 'Recebida'),
            ('CP202401009', 9, 8, '2024-01-22 14:30:00', 1990.00, 'Recebida'),
            ('CP202401010', 10, 1, '2024-01-24 11:00:00', 995.00, 'Em Trânsito'),
            # … outras compras …
        ]),

        # 8) Itens de Compra
        ("""
         INSERT INTO item_compra
           (id_compra,id_produto,quantidade,preco_unitario,valor_total)
         VALUES (%s,%s,%s,%s,%s)
         ON CONFLICT DO NOTHING;
        """, [
            #-- Compra 1 - Samsung
            (1, 1, 10, 2800.00, 28000.00),

            #-- Compra 2 - Dell
            (2, 2, 5, 2300.00, 11500.00),

            #-- Compra 3 - Nestlé
            (3, 7, 50, 20.00, 1000.00),
            (3, 8, 50, 6.50, 325.00),
            (3, 10, 10, 3.00, 30.00),

            #-- Compra 4 - Nike
            (4, 13, 20, 320.00, 6400.00),

            #-- Compra 5 - Tramontina
            (5, 16, 10, 240.00, 2400.00),

            #-- Compra 6 - P&G
            (6, 21, 30, 14.50, 435.00),
            (6, 22, 20, 19.00, 380.00),
            (6, 26, 5, 7.00, 35.00),

            #-- Compra 7 - Mattel
            (7, 37, 20, 120.00, 2400.00),
            (7, 40, 100, 9.90, 990.00),
            (7, 38, 15, 14.00, 210.00),

            #-- Compra 8 - Intrínseca
            (8, 31, 10, 39.00, 390.00),

            #-- Compra 9 - JBL
            (9, 4, 10, 199.00, 1990.00),

            #-- Compra 10 - Melitta
            (10, 6, 50, 19.90, 995.00),
        ]),

        # 9) Estoque
        ("""
         INSERT INTO estoque
           (id_produto,id_loja,quantidade_atual,quantidade_minima,quantidade_maxima)
         VALUES (%s,%s,%s,%s,%s)
         ON CONFLICT (id_produto,id_loja) DO UPDATE
           SET quantidade_atual=EXCLUDED.quantidade_atual,
               quantidade_minima=EXCLUDED.quantidade_minima,
               quantidade_maxima=EXCLUDED.quantidade_maxima;
        """, [
            #-- Loja SP
            (1, 1, 25, 5, 50),
            (2, 1, 15, 3, 30),
            (3, 1, 20, 5, 40),
            (4, 1, 50, 10, 100),
            (5, 1, 45, 10, 80),
            (6, 1, 200, 50, 400),
            (7, 1, 150, 30, 300),

            #-- Loja RJ
            (1, 2, 20, 5, 40),
            (3, 2, 15, 3, 30),
            (8, 2, 180, 40, 350),
            (9, 2, 220, 50, 400),
            (10, 2, 240, 50, 450),
            (11, 2, 30, 10, 60),
            (12, 2, 25, 10, 50),

            #-- Loja BH
            (13, 3, 35, 10, 70),
            (14, 3, 40, 10, 80),
            (15, 3, 30, 10, 60),
            (16, 3, 20, 5, 40),
            (17, 3, 25, 5, 50),
            (18, 3, 15, 5, 30),

            #-- Loja PE
            (19, 4, 8, 2, 15),
            (20, 4, 45, 10, 90),
            (21, 4, 80, 20, 150),
            (22, 4, 90, 20, 180),
            (23, 4, 12, 3, 25),
            (24, 4, 18, 5, 35),

            #-- Loja BA
            (25, 5, 30, 10, 60),
            (26, 5, 35, 10, 70),
            (27, 5, 85, 20, 170),
            (28, 5, 65, 15, 130),
            (29, 5, 50, 10, 100),
            (30, 5, 40, 10, 80),
        ]),

        # 10) Vendas
        ("""
         INSERT INTO venda
           (id_produto,quantidade,valor_total,data_venda)
         VALUES (%s,%s,%s,%s)
         ON CONFLICT DO NOTHING;
        """, [
            (1,  1, 3698.90, '2024-01-15 10:30:00'),
            (2,  1, 449.80,  '2024-01-15 14:45:00'),
            (3,  1, 2199.00, '2024-01-16 11:00:00'),
            (4,  1, 279.80,  '2024-01-17 15:30:00'),
            (5,  1, 519.70,  '2024-01-18 09:15:00'),
            (6,  1, 89.90,   '2024-01-19 16:00:00'),
            (7,  1, 1499.00, '2024-01-20 10:45:00'),
            (8,  1, 349.70,  '2024-01-21 13:20:00'),
            (9,  1, 169.80,  '2024-01-22 11:30:00'),
            (10, 1, 787.50,  '2024-01-23 14:00:00'),
            (11, 1, 4298.80, '2024-02-01 09:30:00'),
            (12, 1, 199.90,  '2024-02-02 15:45:00'),
            (13, 1, 659.60,  '2024-02-03 10:15:00'),
            (14, 1, 89.90,   '2024-02-04 14:30:00'),
            (15, 1, 349.80,  '2024-02-05 11:00:00'),
        ]),

        #fornecedores
        ("""
         INSERT INTO fornecedor
           (cnpj, razao_social, nome_fantasia, telefone, email, endereco, cidade, estado, ativo)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
         ON CONFLICT DO NOTHING;
        """, [
            ('12345678000100', 'Samsung Eletrônicos do Brasil LTDA', 'Samsung Brasil', '11-5644-2000', 'contato@samsung.com.br', 'Av. Dr. Chucri Zaidan, 1240', 'São Paulo', 'SP', True),
            ('23456789000111', 'Dell Computadores do Brasil LTDA', 'Dell Brasil', '11-5503-5000', 'vendas@dell.com.br', 'Av. Industrial, 700', 'Eldorado do Sul', 'RS', True),
            ('34567890000122', 'Nestlé Brasil LTDA', 'Nestlé', '11-2199-2999', 'faleconosco@nestle.com.br', 'Av. Nações Unidas, 12495', 'São Paulo', 'SP', True),
            ('45678901000133', 'Nike do Brasil Com. e Part. LTDA', 'Nike Brasil', '11-5102-4400', 'atendimento@nike.com.br', 'Av. das Nações Unidas, 14261', 'São Paulo', 'SP', True),
            ('56789012000144', 'Tramontina S.A.', 'Tramontina', '54-3461-8200', 'sac@tramontina.com.br', 'Rod. RS-324 Km 2,5', 'Carlos Barbosa', 'RS', True),
            ('67890123000155', 'Procter & Gamble do Brasil S.A.', 'P&G Brasil', '11-3046-5800', 'atendimento@pg.com.br', 'Av. Brigadeiro Faria Lima, 3900', 'São Paulo', 'SP', True),
            ('78901234000166', 'Mattel do Brasil LTDA', 'Mattel', '11-5090-8500', 'sac@mattel.com.br', 'Av. Tamboré, 1400', 'Barueri', 'SP', True),
            ('89012345000177', 'Editora Intrínseca LTDA', 'Intrínseca', '21-2206-7400', 'contato@intrinseca.com.br', 'Rua Marquês de São Vicente, 99', 'Rio de Janeiro', 'RJ', True),
            ('90123456000188', 'JBL do Brasil', 'JBL', '11-3048-1700', 'suporte@jbl.com.br', 'Rua James Clerk Maxwell, 170', 'Campinas', 'SP', True),
            ('01234567000199', 'Melitta do Brasil', 'Melitta', '47-3801-5000', 'sac@melitta.com.br', 'Rua Dona Francisca, 8300', 'Joinville', 'SC', True),
        ]),

        #clientes
        ("""
         INSERT INTO clientes
           (cpf, nome, email, telefone, endereco, cidade, estado, cep)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
         ON CONFLICT DO NOTHING;
        """, [
            ('12345678901', 'Paulo Henrique Silva', 'paulo.silva@email.com', '11-98765-4321', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234567', True),
            ('23456789012', 'Ana Maria Santos', 'ana.santos@email.com', '11-97654-3210', 'Av. Paulista, 456', 'São Paulo', 'SP', '01310100', True),
            ('34567890123', 'Roberto Carlos Oliveira', 'roberto.oliveira@email.com', '21-96543-2109', 'Rua Copacabana, 789', 'Rio de Janeiro', 'RJ', '22020050', True),
            ('45678901234', 'Juliana Costa Lima', 'juliana.lima@email.com', '31-95432-1098', 'Av. Afonso Pena, 321', 'Belo Horizonte', 'MG', '30130005', True),
            ('56789012345', 'Fernando Alves Costa', 'fernando.costa@email.com', '81-94321-0987', 'Av. Boa Viagem, 654', 'Recife', 'PE', '51020180', True),
            ('67890123456', 'Mariana Ferreira Souza', 'mariana.souza@email.com', '71-93210-9876', 'Av. Oceânica, 987', 'Salvador', 'BA', '40160060', True),
            ('78901234567', 'Alexandre Martins Silva', 'alexandre.silva@email.com', '51-92109-8765', 'Rua da Praia, 147', 'Porto Alegre', 'RS', '90020060', True),
            ('89012345678', 'Camila Rodrigues Santos', 'camila.santos@email.com', '61-91098-7654', 'SQS 308 Bloco C', 'Brasília', 'DF', '70355030', True),
            ('90123456789', 'Ricardo Pereira Lima', 'ricardo.lima@email.com', '41-90987-6543', 'Rua XV de Novembro, 258', 'Curitiba', 'PR', '80020310', True),
            ('01234567890', 'Patricia Almeida Costa', 'patricia.costa@email.com', '11-89876-5432', 'Alameda Santos, 369', 'São Paulo', 'SP', '01419002', True),
            ('11223344556', 'Bruno Carvalho Dias', 'bruno.dias@email.com', '21-88765-4321', 'Av. Rio Branco, 741', 'Rio de Janeiro', 'RJ', '20040008', True),
            ('22334455667', 'Letícia Nunes Oliveira', 'leticia.oliveira@email.com', '31-87654-3210', 'Rua da Bahia, 852', 'Belo Horizonte', 'MG', '30160011', True),
            ('33445566778', 'Carlos Eduardo Santos', 'carlos.santos@email.com', '81-86543-2109', 'Rua do Sol, 963', 'Recife', 'PE', '50030230', True),
            ('44556677889', 'Daniela Sousa Lima', 'daniela.lima@email.com', '71-85432-1098', 'Av. Sete de Setembro, 159', 'Salvador', 'BA', '40060500', True),
            ('55667788990', 'Marcelo Ferreira Costa', 'marcelo.costa@email.com', '51-84321-0987', 'Av. Ipiranga, 753', 'Porto Alegre', 'RS', '90160091', True),
        ]),

        #item-compra
        ("""
         INSERT INTO item_compra
            (id_compra,id_produto,quantidade,preco_unitario,valor_total)
        VALUES(%s,%s,%s,%s,%s)
         ON CONFLICT DO NOTHING;
        """, [
            (1,  1,  10, 2800.00, 28000.00),
            #-- Compra 2 - Dell
            (2,  2,   5, 2300.00, 11500.00),
            #-- Compra 3 - Nestlé
            (3,  7,  50,   20.00,  1000.00),
            (3,  8,  50,    6.50,   325.00),
            (3, 10,  10,    3.00,    30.00),
            #-- Compra 4 - Nike
            (4, 13,  20,  320.00,  6400.00),
            #-- Compra 5 - Tramontina
            (5, 16,  10,  240.00,  2400.00),
            #-- Compra 6 - P&G
            (6, 21,  30,   14.50,   435.00),
            (6, 22,  20,   19.00,   380.00),
            (6, 26,   5,    7.00,    35.00),
            #-- Compra 7 - Mattel
            (7, 37,  20,  120.00,  2400.00),
            (7, 40, 100,    9.90,   990.00),
            (7, 38,  15,   14.00,   210.00),
            #-- Compra 8 - Intrínseca
            (8, 31,  10,   39.00,   390.00),
            #-- Compra 9 - JBL
            (9,  4,  10,  199.00,  1990.00),
            #-- Compra 10 - Melitta
            (10, 6,  50,   19.90,   995.00),
        ]),
    ]

    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            for sql, params in inserts:
                cur.executemany(sql, params)
    conn.close()
    # finalmente, copia tudo para o ZODB
    migrar_tudo_para_zodb()

def test_system():
    test_integracao()

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
    'teste':('Testar Integridade do Sistema', test_system),
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
