from app.services.questionario_service import QuestionarioService


class QuestionarioController:

    def __init__(self):
        self.questionario_service = QuestionarioService()

    def salvar_questionario(self, aluno_id, dados):
        try:
            valido, erro, status = self.questionario_service.validar_questionario(dados)
            if not valido:
                return erro, status

            titulo = dados.get('titulo', 'Questionário de Nivelamento')
            respostas = dados.get('respostas', {})

            resposta, status = self.questionario_service.salvar(aluno_id, titulo, respostas)
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500

    def listar_questionarios(self, aluno_id):
        try:
            resposta, status = self.questionario_service.listar(aluno_id)
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500
