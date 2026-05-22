from app.services.auth_service import AuthService


class AuthController:

    def __init__(self):
        self.auth_service = AuthService()

    def cadastrar(self, dados):
        try:
            nome = dados.get('nome')
            email = dados.get('email')
            senha = dados.get('senha')

            valido, erro, status = self.auth_service.validar_cadastro(nome, email, senha)
            if not valido:
                return erro, status

            resposta, status = self.auth_service.registrar_aluno(nome, email, senha)
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500

    def login(self, dados):
        try:
            email = dados.get('email')
            senha = dados.get('senha')

            resposta, status = self.auth_service.autenticar_aluno(email, senha)
            if resposta is None:
                return status, status  # retorna erro
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500

    def obter_perfil(self, aluno_id):
        try:
            resposta, status = self.auth_service.obter_dados_perfil(aluno_id)
            if resposta is None:
                return status, status  # retorna erro
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500
