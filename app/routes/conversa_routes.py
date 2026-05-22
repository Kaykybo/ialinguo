from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import ConversaController

conversa_bp = Blueprint('conversa', __name__)
conversa_controller = ConversaController()


@conversa_bp.route('/contextos', methods=['GET'])
@jwt_required()
def listar_contextos():
    resposta, status = conversa_controller.listar_contextos()
    return jsonify(resposta), status


@conversa_bp.route('/iniciar', methods=['POST'])
@jwt_required()
def iniciar_conversa_route():
    aluno_id = int(get_jwt_identity())
    dados = request.get_json() or {}
    resposta, status = conversa_controller.iniciar_conversa(aluno_id, dados)
    return jsonify(resposta), status


@conversa_bp.route('/<int:conversa_id>/enviar', methods=['POST'])
@jwt_required()
def enviar_mensagem(conversa_id):
    aluno_id = int(get_jwt_identity())
    dados = request.get_json()
    resposta, status = conversa_controller.enviar_mensagem(conversa_id, aluno_id, dados)
    return jsonify(resposta), status


@conversa_bp.route('/<int:conversa_id>/finalizar', methods=['POST'])
@jwt_required()
def finalizar_conversa(conversa_id):
    aluno_id = int(get_jwt_identity())
    resposta, status = conversa_controller.finalizar_conversa(conversa_id, aluno_id)
    return jsonify(resposta), status
