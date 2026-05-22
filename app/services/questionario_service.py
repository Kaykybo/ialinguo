from app import db
from app.db_queries import salvar_questionario, listar_questionarios_aluno


class QuestionarioService:

    @staticmethod
    def validar_questionario(dados):
        if not dados:
            return None, {'erro': 'Dados não fornecidos'}, 400
        return True, None, None

    @staticmethod
    def salvar(aluno_id, titulo, respostas):
        novo_questionario = salvar_questionario(aluno_id, titulo, respostas)

        return {
            'mensagem': 'Questionário salvo com sucesso',
            'questionario_id': novo_questionario.id
        }, 201

    @staticmethod
    def listar(aluno_id):
        questionarios = listar_questionarios_aluno(aluno_id)
        return {'questionarios': [q.to_dict() for q in questionarios]}, 200
