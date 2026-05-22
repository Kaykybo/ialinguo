from app.services.historico_service import HistoricoService


class HistoricoController:

    def __init__(self):
        self.historico_service = HistoricoService()

    def listar_historico_conversas(self, aluno_id):
        try:
            resposta, status = self.historico_service.listar_conversas(aluno_id)
            return resposta, status
        except Exception as e:
            return {'erro': str(e)}, 500

    def detalhes_conversa(self, conversa_id, aluno_id):
        try:
            resposta, status = self.historico_service.obter_detalhes_conversa(conversa_id, aluno_id)
            if resposta is None:
                return status, status  # retorna erro
            return resposta, status
        except Exception as e:
            return {'erro': str(e)}, 500
