import requests
from kivy.app import App


class MyFirebase():
    CHAVE_API = "AIzaSyAdAtVgOR2qNq17xJuVqSnd0Ats2G3cfHQ"


    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.CHAVE_API}"
        print(email, senha)

        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}

        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            print("Usúario Criado")
            # requisicao_dic["idToken"] -> autenticação
            # requisicao_dic["refreshToken"] -> token que mantem o usúario logado
            # requisicao_dic["localId"] -> id_usúario
            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            req_id = requests.get(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={self.id_token}")
            id_vendedor = req_id.json()


            # Cria um Usuário
            link = f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)

            # Atualizar o valor do próximo usuário
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://aplicativovendas-58efb-default-rtdb.firebaseio.com/.json?auth={self.id_token}", data=info_id_vendedor)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")


        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagen_login"].text = mensagem_erro
            pagina_login.ids["mensagen_login"].color = (1, 0, 0, 1)


    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.CHAVE_API}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}

        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            refresh_token = requisicao_dic["refreshToken"] #-> token que mantem o usúario logado
            local_id = requisicao_dic["localId"] #-> id_usúario
            id_token = requisicao_dic["idToken"] #-> autenticação

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")


        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagen_login"].text = mensagem_erro
            pagina_login.ids["mensagen_login"].color = (1, 0, 0, 1)


    # Mantem o usuário logado
    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.CHAVE_API}"
        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic["user_id"]
        id_token = requisicao_dic["id_token"]
        print(requisicao_dic)

        return local_id, id_token