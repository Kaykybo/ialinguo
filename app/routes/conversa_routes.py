from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.db_queries import (iniciar_conversa as criar_conversa, buscar_conversa_ativa,
                            adicionar_mensagem, criar_feedback, finalizar_conversa as finalizar_conversa_db)
from app.services import AIService
from datetime import datetime

conversa_bp = Blueprint('conversa', __name__)

_ai_service = AIService()


@conversa_bp.route('/contextos', methods=['GET'])
@jwt_required()
def listar_contextos():
    contextos = [
        {
            'id': k,
            'nome': k.replace('_', ' ').title(),
            'descricao': v[:100] + '...' if len(v) > 100 else v
        }
        for k, v in AIService.CONTEXTOS.items()
    ]
    return jsonify({'contextos': contextos}), 200


@conversa_bp.route('/iniciar', methods=['POST'])
@jwt_required()
def iniciar_conversa_route():
    try:
        aluno_id = int(get_jwt_identity())
        dados = request.get_json() or {}

        contexto = dados.get('contexto', 'conversa livre')
        if contexto not in AIService.CONTEXTOS:
            contexto = 'conversa livre'

        nova_conversa = criar_conversa(aluno_id, contexto)

        msg_inicial = f"Hello! I'm your English practice partner. We will speak only in English in a {contexto} context. If you use Portuguese or any other language, I will remind you and this will lower your fluency score. How can I help you today?"
        adicionar_mensagem(nova_conversa.id, 'ia', msg_inicial)

        return jsonify({
            'conversa_id': nova_conversa.id,
            'mensagem_inicial': msg_inicial,
            'contexto': contexto
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@conversa_bp.route('/<int:conversa_id>/enviar', methods=['POST'])
@jwt_required()
def enviar_mensagem(conversa_id):
    try:
        aluno_id = int(get_jwt_identity())
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        mensagem_texto = dados.get('mensagem')
        tipo = dados.get('tipo', 'texto')

        conversa = buscar_conversa_ativa(conversa_id, aluno_id)

        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada ou já finalizada'}), 404

        if not mensagem_texto:
            return jsonify({'erro': 'Mensagem vazia'}), 400

        msg_aluno = adicionar_mensagem(conversa.id, 'aluno', mensagem_texto, tipo)

        historico_lista = conversa.get_historico_lista(limite=10)

        resposta_ia = _ai_service.gerar_resposta(
            mensagem_aluno=mensagem_texto,
            contexto=conversa.contexto,
            historico=historico_lista
        )

        msg_ia = adicionar_mensagem(conversa.id, 'ia', resposta_ia)

        return jsonify({
            'resposta': resposta_ia,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@conversa_bp.route('/<int:conversa_id>/finalizar', methods=['POST'])
@jwt_required()
def finalizar_conversa(conversa_id):
    try:
        aluno_id = int(get_jwt_identity())

        conversa = buscar_conversa_ativa(conversa_id, aluno_id)

        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada'}), 404

        texto_conversa = conversa.get_texto_completo()
        feedback_data = _ai_service.gerar_feedback(texto_conversa, conversa.contexto)

        # Formatar pontos positivos e melhorias como strings
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

        return jsonify({
            'mensagem': 'Conversa finalizada com sucesso',
            'feedback': novo_feedback.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
