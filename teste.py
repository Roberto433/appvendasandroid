vendas = {"id1": {"cliente": "roberto", "produto": "Iphone" }}

for id_venda in vendas:
    venda = vendas[id_venda]
    print(venda['cliente'])

