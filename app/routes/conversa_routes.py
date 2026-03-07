from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Conversa, Mensagem, Feedback
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
def iniciar_conversa():
    try:
        aluno_id = int(get_jwt_identity())
        dados = request.get_json() or {}

        contexto = dados.get('contexto', 'conversa livre')
        if contexto not in AIService.CONTEXTOS:
            contexto = 'conversa livre'

        nova_conversa = Conversa(aluno_id=aluno_id, contexto=contexto, status='ativa')
        db.session.add(nova_conversa)
        db.session.commit()

        msg_inicial = f"Hello! I'm your AI assistant. Let's practice English in a {contexto} context. How can I help you today?"

        mensagem_ia = Mensagem(conversa_id=nova_conversa.id, remetente='ia', texto=msg_inicial)
        db.session.add(mensagem_ia)
        db.session.commit()

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

        conversa = Conversa.query.filter_by(
            id=conversa_id,
            aluno_id=aluno_id,
            status='ativa'
        ).first()

        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada ou já finalizada'}), 404

        if not mensagem_texto:
            return jsonify({'erro': 'Mensagem vazia'}), 400

        msg_aluno = Mensagem(conversa_id=conversa.id, remetente='aluno', texto=mensagem_texto, tipo=tipo)
        db.session.add(msg_aluno)

        historico_lista = conversa.get_historico_lista(limite=10)

        resposta_ia = _ai_service.gerar_resposta(
            mensagem_aluno=mensagem_texto,
            contexto=conversa.contexto,
            historico=historico_lista
        )

        msg_ia = Mensagem(conversa_id=conversa.id, remetente='ia', texto=resposta_ia)
        db.session.add(msg_ia)
        db.session.commit()

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

        conversa = Conversa.query.filter_by(
            id=conversa_id,
            aluno_id=aluno_id,
            status='ativa'
        ).first()

        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada'}), 404

        texto_conversa = conversa.get_texto_completo()
        feedback_data = _ai_service.gerar_feedback(texto_conversa, conversa.contexto)

        novo_feedback = Feedback(
            conversa_id=conversa.id,
            pontos_positivos=feedback_data.get('pontos_positivos', ''),
            pontos_melhoria=feedback_data.get('pontos_melhoria', ''),
            nota_fluencia=feedback_data.get('nota_fluencia', 5)
        )

        conversa.finalizar()

        db.session.add(novo_feedback)
        db.session.commit()

        return jsonify({
            'mensagem': 'Conversa finalizada com sucesso',
            'feedback': novo_feedback.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
