class Produto:
    def __init__(self, nome, categoria, marca, preco, estoque):
        self.nome = nome
        self.categoria = categoria
        self.marca = marca
        self.preco = preco
        self.estoque = estoque

    def __repr__(self):
        return f"{self.nome} ({self.marca}) - R${self.preco:.2f}"
