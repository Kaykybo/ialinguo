from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db_queries import (listar_conversas_aluno, buscar_conversa_por_id,
                            listar_mensagens_conversa, buscar_feedback_conversa)

historico_bp = Blueprint('historico', __name__)


@historico_bp.route('/conversas', methods=['GET'])
@jwt_required()
def listar_historico_conversas():
    try:
        aluno_id = int(get_jwt_identity())

        conversas = listar_conversas_aluno(aluno_id)

        return jsonify({'historico': [c.to_dict() for c in conversas]}), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@historico_bp.route('/conversas/<int:conversa_id>', methods=['GET'])
@jwt_required()
def detalhes_conversa(conversa_id):
    try:
        aluno_id = int(get_jwt_identity())

        conversa = buscar_conversa_por_id(conversa_id, aluno_id)

        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada'}), 404

        mensagens = listar_mensagens_conversa(conversa.id)

        feedback = buscar_feedback_conversa(conversa.id)

        return jsonify({
            'conversa': {
                'id': conversa.id,
                'contexto': conversa.contexto,
                'data_inicio': conversa.data_inicio.isoformat(),
                'data_fim': conversa.data_fim.isoformat() if conversa.data_fim else None,
                'status': conversa.status
            },
            'mensagens': [m.to_dict() for m in mensagens],
            'feedback': feedback.to_dict() if feedback else None
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
