from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import HistoricoController

historico_bp = Blueprint('historico', __name__)
historico_controller = HistoricoController()


@historico_bp.route('/conversas', methods=['GET'])
@jwt_required()
def listar_historico_conversas():
    aluno_id = int(get_jwt_identity())
    resposta, status = historico_controller.listar_historico_conversas(aluno_id)
    return jsonify(resposta), status


@historico_bp.route('/conversas/<int:conversa_id>', methods=['GET'])
@jwt_required()
def detalhes_conversa(conversa_id):
    aluno_id = int(get_jwt_identity())
    resposta, status = historico_controller.detalhes_conversa(conversa_id, aluno_id)
    return jsonify(resposta), status
