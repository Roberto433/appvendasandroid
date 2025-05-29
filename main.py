from kivy.app import App
from kivy.lang import Builder
from myfirebase import MyFirebase
from telas import *
from botoes import *
from bannervenda import BannerVenda
import requests
import os
import certifi
from functools import partial
from bannervendedor import BannerVendedor
from datetime import date

os.environ["SSL_CERT_FILE"] = certifi.where()

GUI = Builder.load_file("main.kv")
class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase()
        return GUI


    def on_start(self):

        # carregar as fotos de perfil
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil,
                                                                                          foto))
            lista_fotos.add_widget(imagem)

        # Carregar as Fotos dos Clientes
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}",
                                 on_release=partial(self.selecionar_cliente, foto_cliente))
            label_cliente = LabelButton(text=foto_cliente.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label_cliente)


        # Carregar as Fotos dos Produtos
        arquivos = os.listdir("icones/fotos_produtos")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}",
                                 on_release=partial(self.selecionar_produto, foto_produto))
            label_produto = LabelButton(text=foto_produto.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label_produto)

        # Carregar a data
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        label_data = pagina_adicionarvendas.ids["label_data"]
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"


        # carrega as infos do usúario
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # pegar informações do usúario
            requisicao = requests.get(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()

            # preecher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            # Preencher o ID único
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_vendedor"].text = f"Seu ID Único: {id_vendedor}"

            # Preencher o total de Vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#<000000>]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            # Preecher Equipe
            self.equipe = requisicao_dic["equipe"]

            # preecher lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids["homepage"]
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                         produto=venda["produto"], foto_produto=venda["foto_produto"],
                                         data=venda["data"], preco=venda["preco"], unidade=venda["unidade"],
                                         quantidade=venda["quantidade"])

                    lista_vendas.add_widget(banner)
            except Exception as excecao:
                print(excecao)

            # Preecher equipe Vendedores
            equipe = requisicao_dic["equipe"]
            lista_equipe = equipe.split(",")
            pagina_listavendedores = self.root.ids["listarvendedorpage"]
            lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)


            self.mudar_tela("homepage")

        except:
            pass

    def mudar_tela(self, id_tela):
        print(id_tela)
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    # Atualizar no Bamco de Dados
    def mudar_foto_perfil(self, foto, *args):
        print(foto)
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"
        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                    data=info)
        print(requisicao.json())
        self.mudar_tela("ajustespage")

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendas-58efb-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        print(requisicao_dic)
        pagina_adicionarvendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adicionarvendedor.ids["mensagem_outrovendedor"]
        if requisicao_dic == {}:
            mensagem_texto.text = "Usuário não encontrado"
        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor jà faz parte da Equipe"
            else:
                info = f'{{"equipe": "{self.equipe}"}}'
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                requests.patch(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                               data=info)
                mensagem_texto.text = "Vendedor Adicionado com Sucesso"
                # Adicionar um novo banner na lista de Vendedores
                pagina_listavendedores = self.root.ids["listarvendedorpage"]
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *kwargs):
        self.cliente = foto.replace(".png", "")
        # Pintar de branco todas as outras letras
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            # Pintar de azul a letra do item que selecionamos
            # foto -> carrefour.png / Label -> Carrefour -> carrefour -> carrefour.png
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/275, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *kwargs):
        self.produto = foto.replace(".png", "")
        # Pintar de branco todas as outras letras
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            # Pintar de azul a letra do item que selecionamos
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/275, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        # Pintar de branco todas as outras letras
        self.unidade = id_label.replace("unidades_", "")
        pagina_adicionarvendas.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)

        # Pintar de azul a letra do item que selecionamos
        pagina_adicionarvendas.ids[id_label].color = (0, 207/275, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids["preco_total"].text
        quantidade = pagina_adicionarvendas.ids["quantidade"].text

        if not cliente:
            pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_litros"].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)

        if not quantidade:
            pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)

        # Dado que ele preecheu tudo, vamos executar o código de adicionar venda

        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"

            preco = preco * quantidade
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", '\
                    f'"foto_produto": "{foto_produto}","data": "{data}", "unidade": "{unidade}",'\
                    f'"preco": "{preco}","quantidade": "{quantidade}"}}'
            requests.post(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}",
                           data=info)

            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto,
                                 data=data, preco=preco, quantidade=quantidade, unidade=unidade)
            pagina_homepage = self.root.ids["homepage"]
            lista_vendas = pagina_homepage.ids["lista_vendas"]
            lista_vendas.add_widget(banner)

            requisicao = requests.get(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            total_vendas = float(requisicao.json())
            total_vendas += preco
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                           data=info)
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#<000000>]Total de Vendas:[/color] [b]R${total_vendas}[/b]"
            self.mudar_tela("homepage")

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_totalvendas = self.root.ids["totalvendaspage"]
        lista_vendas = pagina_totalvendas.ids["lista_vendas"]
        for item in list(lista_vendas.children): # Remove lista duplicada
            lista_vendas.remove_widget(item)

        # Preencher Página todalvendaspage
        # Pegar informações da empresa
        requisicao = requests.get(f'https://aplicativovendas-58efb-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()

        # preecher foto de perfil
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/hash.png"

        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda["preco"])
                    banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'],
                                         foto_produto=venda['foto_produto'],data=venda['data'], preco=venda['preco'],
                                         quantidade=venda['quantidade'], unidade=venda['unidade'])
                    lista_vendas.add_widget(banner)
            except:
                pass

        # Preencher o total de Vendas

        pagina_totalvendas.ids["label_total_vendas"].text = f"[color=#<000000>]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

        #Redirecionar para totalvendaspage
        self.mudar_tela('totalvendaspage')

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"

        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):


        try:
            vendas = dic_info_vendedor["vendas"]
            pagina_vendasoutrovendedor = self.root.ids['vendasoutrovendedorpage']
            lista_vendas = pagina_vendasoutrovendedor.ids['lista_vendas']
            # Limpar Vendas anteriores
            for item in list(lista_vendas.children):  # Remove vendas duplicada
                lista_vendas.remove_widget(item)

            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'],
                                     foto_produto=venda['foto_produto'],data=venda['data'], preco=venda['preco'],
                                     quantidade=venda['quantidade'], unidade=venda['unidade'])
                lista_vendas.add_widget(banner)
        except:
            pass
        total_vendas = dic_info_vendedor["total_vendas"]
        pagina_vendasoutrovendedor.ids["label_total_vendas"].text = f"[color=#<000000>]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

        self.mudar_tela("vendasoutrovendedorpage")


MainApp().run()