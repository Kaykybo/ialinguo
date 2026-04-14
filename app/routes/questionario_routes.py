from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db_queries import salvar_questionario, listar_questionarios_aluno

questionario_bp = Blueprint('questionario', __name__)


@questionario_bp.route('', methods=['POST'])
@jwt_required()
def salvar_questionario():
    try:
        aluno_id = int(get_jwt_identity())
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        titulo = dados.get('titulo', 'Questionário de Nivelamento')
        respostas = dados.get('respostas', {})

        novo_questionario = salvar_questionario(aluno_id, titulo, respostas)

        return jsonify({
            'mensagem': 'Questionário salvo com sucesso',
            'questionario_id': novo_questionario.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@questionario_bp.route('', methods=['GET'])
@jwt_required()
def listar_questionarios():
    try:
        aluno_id = int(get_jwt_identity())

        questionarios = listar_questionarios_aluno(aluno_id)

        return jsonify({'questionarios': [q.to_dict() for q in questionarios]}), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
