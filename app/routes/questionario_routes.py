from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import QuestionarioController

questionario_bp = Blueprint('questionario', __name__)
questionario_controller = QuestionarioController()


@questionario_bp.route('', methods=['POST'])
@jwt_required()
def salvar_questionario():
    aluno_id = int(get_jwt_identity())
    dados = request.get_json()
    resposta, status = questionario_controller.salvar_questionario(aluno_id, dados)
    return jsonify(resposta), status


@questionario_bp.route('', methods=['GET'])
@jwt_required()
def listar_questionarios():
    aluno_id = int(get_jwt_identity())
    resposta, status = questionario_controller.listar_questionarios(aluno_id)
    return jsonify(resposta), status
