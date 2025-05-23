# utils/analises.py

def exibir_vendas_por_trimestre(vendas):
    print("Ano | Trim | Total de vendas")
    print("---------------------------")
    for r in vendas:
        print(f"{int(r['ano'])}  |  {int(r['trimestre'])}   | R${r['total']:.2f}")

def exibir_comentarios(coms):
    for c in coms:
        print(f"[{c['data']}] {c['cliente']}: {c['comentario']}")
        if "imagens" in c:
            for url in c["imagens"]:
                print("  📷", url)
