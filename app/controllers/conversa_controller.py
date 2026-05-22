from app.services.conversa_service import ConversaService


class ConversaController:

    def __init__(self):
        self.conversa_service = ConversaService()

    def listar_contextos(self):
        try:
            contextos = self.conversa_service.obter_contextos()
            return {'contextos': contextos}, 200
        except Exception as e:
            return {'erro': str(e)}, 500

    def iniciar_conversa(self, aluno_id, dados):
        try:
            contexto = dados.get('contexto', 'conversa livre')
            resposta = self.conversa_service.iniciar(aluno_id, contexto)
            return resposta, 201
        except Exception as e:
            return {'erro': str(e)}, 500

    def enviar_mensagem(self, conversa_id, aluno_id, dados):
        try:
            if not dados:
                return {'erro': 'Dados não fornecidos'}, 400

            mensagem_texto = dados.get('mensagem')
            tipo = dados.get('tipo', 'texto')

            resposta, status = self.conversa_service.processar_mensagem(conversa_id, aluno_id, mensagem_texto, tipo)
            if resposta is None:
                return status, status  # retorna erro
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500

    def finalizar_conversa(self, conversa_id, aluno_id):
        try:
            resposta, status = self.conversa_service.finalizar(conversa_id, aluno_id)
            if resposta is None:
                return status, status  # retorna erro
            return resposta, status

        except Exception as e:
            return {'erro': str(e)}, 500
