from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import AuthController
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
auth_controller = AuthController()


@auth_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@auth_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.get_json()
    resposta, status = auth_controller.cadastrar(dados)
    return jsonify(resposta), status


@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    resposta, status = auth_controller.login(dados)
    return jsonify(resposta), status


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def perfil():
    aluno_id = int(get_jwt_identity())
    resposta, status = auth_controller.obter_perfil(aluno_id)
    return jsonify(resposta), status
