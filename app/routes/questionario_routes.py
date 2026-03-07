from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Questionario

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

        novo_questionario = Questionario(aluno_id=aluno_id, titulo=titulo, respostas=respostas)
        db.session.add(novo_questionario)
        db.session.commit()

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

        questionarios = Questionario.query.filter_by(aluno_id=aluno_id)\
            .order_by(Questionario.data_preenchimento.desc())\
            .all()

        return jsonify({'questionarios': [q.to_dict() for q in questionarios]}), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
