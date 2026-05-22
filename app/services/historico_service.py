from app.db_queries import (listar_conversas_aluno, buscar_conversa_por_id,
                            listar_mensagens_conversa, buscar_feedback_conversa)


class HistoricoService:

    @staticmethod
    def listar_conversas(aluno_id):
        conversas = listar_conversas_aluno(aluno_id)
        return {'historico': [c.to_dict() for c in conversas]}, 200

    @staticmethod
    def obter_detalhes_conversa(conversa_id, aluno_id):
        conversa = buscar_conversa_por_id(conversa_id, aluno_id)

        if not conversa:
            return None, {'erro': 'Conversa não encontrada'}, 404

        mensagens = listar_mensagens_conversa(conversa.id)
        feedback = buscar_feedback_conversa(conversa.id)

        return {
            'conversa': {
                'id': conversa.id,
                'contexto': conversa.contexto,
                'data_inicio': conversa.data_inicio.isoformat(),
                'data_fim': conversa.data_fim.isoformat() if conversa.data_fim else None,
                'status': conversa.status
            },
            'mensagens': [m.to_dict() for m in mensagens],
            'feedback': feedback.to_dict() if feedback else None
        }, 200
