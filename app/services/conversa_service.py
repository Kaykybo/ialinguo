from app import db
from app.db_queries import (iniciar_conversa as criar_conversa, buscar_conversa_ativa,
                            adicionar_mensagem, criar_feedback, finalizar_conversa as finalizar_conversa_db)
from app.services.ai_service import AIService


class ConversaService:

    def __init__(self):
        self.ai_service = AIService()

    def obter_contextos(self):
        contextos = [
            {
                'id': k,
                'nome': k.replace('_', ' ').title(),
                'descricao': v[:100] + '...' if len(v) > 100 else v
            }
            for k, v in AIService.CONTEXTOS.items()
        ]
        return contextos

    def iniciar(self, aluno_id, contexto):
        if contexto not in AIService.CONTEXTOS:
            contexto = 'conversa livre'

        nova_conversa = criar_conversa(aluno_id, contexto)

        msg_inicial = f"Hello! I'm your English practice partner. We will speak only in English in a {contexto} context. If you use Portuguese or any other language, I will remind you and this will lower your fluency score. How can I help you today?"
        adicionar_mensagem(nova_conversa.id, 'ia', msg_inicial)

        return {
            'conversa_id': nova_conversa.id,
            'mensagem_inicial': msg_inicial,
            'contexto': contexto
        }

    def processar_mensagem(self, conversa_id, aluno_id, mensagem_texto, tipo='texto'):
        conversa = buscar_conversa_ativa(conversa_id, aluno_id)

        if not conversa:
            return None, {'erro': 'Conversa não encontrada ou já finalizada'}, 404

        if not mensagem_texto:
            return None, {'erro': 'Mensagem vazia'}, 400

        adicionar_mensagem(conversa.id, 'aluno', mensagem_texto, tipo)
        historico_lista = conversa.get_historico_lista(limite=10)

        resposta_ia = self.ai_service.gerar_resposta(
            mensagem_aluno=mensagem_texto,
            contexto=conversa.contexto,
            historico=historico_lista
        )

        adicionar_mensagem(conversa.id, 'ia', resposta_ia)

        from datetime import datetime
        return {
            'resposta': resposta_ia,
            'timestamp': datetime.utcnow().isoformat()
        }, 200

    def finalizar(self, conversa_id, aluno_id):
        conversa = buscar_conversa_ativa(conversa_id, aluno_id)

        if not conversa:
            return None, {'erro': 'Conversa não encontrada'}, 404

        texto_conversa = conversa.get_texto_completo()
        feedback_data = self.ai_service.gerar_feedback(texto_conversa, conversa.contexto)

        pontos_positivos = feedback_data.get('pontos_positivos', '')
        pontos_melhoria = feedback_data.get('pontos_melhoria', '')

        if isinstance(pontos_positivos, dict):
            pontos_positivos = '\n'.join([f"{k}: {v}" for k, v in pontos_positivos.items()])
        elif isinstance(pontos_positivos, list):
            pontos_positivos = '\n'.join(pontos_positivos)

        if isinstance(pontos_melhoria, dict):
            pontos_melhoria = '\n'.join([f"{k}: {v}" for k, v in pontos_melhoria.items()])
        elif isinstance(pontos_melhoria, list):
            pontos_melhoria = '\n'.join(pontos_melhoria)

        novo_feedback = criar_feedback(
            conversa_id=conversa.id,
            pontos_positivos=pontos_positivos,
            pontos_melhoria=pontos_melhoria,
            nota_fluencia=feedback_data.get('nota_fluencia', 5)
        )

        finalizar_conversa_db(conversa)

        return {
            'mensagem': 'Conversa finalizada com sucesso',
            'feedback': novo_feedback.to_dict()
        }, 200
