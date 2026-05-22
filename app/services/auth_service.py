from flask_jwt_extended import create_access_token
from datetime import timedelta
from app.db_queries import buscar_aluno_por_email, buscar_aluno_por_id, cadastrar_aluno


class AuthService:

    @staticmethod
    def validar_cadastro(nome, email, senha):
        if not nome or len(nome) < 3:
            return None, {'erro': 'Nome inválido'}, 400

        if not email or '@' not in email:
            return None, {'erro': 'Email inválido'}, 400

        if not senha or len(senha) < 6:
            return None, {'erro': 'Senha deve ter 6+ caracteres'}, 400

        if buscar_aluno_por_email(email):
            return None, {'erro': 'Email já cadastrado'}, 409

        return True, None, None

    @staticmethod
    def registrar_aluno(nome, email, senha):
        novo_aluno = cadastrar_aluno(nome, email, senha)
        return {
            'mensagem': 'Cadastro realizado!',
            'aluno_id': novo_aluno.id
        }, 201

    @staticmethod
    def autenticar_aluno(email, senha):
        aluno = buscar_aluno_por_email(email)

        if not aluno or not aluno.check_senha(senha):
            return None, {'erro': 'Email ou senha inválidos'}, 401

        access_token = create_access_token(
            identity=str(aluno.id),
            expires_delta=timedelta(days=7)
        )

        return {
            'access_token': access_token,
            'aluno': {
                'id': aluno.id,
                'nome': aluno.nome_completo,
                'email': aluno.email
            }
        }, 200

    @staticmethod
    def obter_dados_perfil(aluno_id):
        aluno = buscar_aluno_por_id(aluno_id)

        if not aluno:
            return None, {'erro': 'Usuário não encontrado'}, 404

        return aluno.to_dict(), 200
