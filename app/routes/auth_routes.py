from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.db_queries import buscar_aluno_por_email, buscar_aluno_por_id, cadastrar_aluno
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/health', methods=['GET'])
def health_check():
    from datetime import datetime
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@auth_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        dados = request.get_json()

        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')

        if not nome or len(nome) < 3:
            return jsonify({'erro': 'Nome inválido'}), 400

        if not email or '@' not in email:
            return jsonify({'erro': 'Email inválido'}), 400

        if not senha or len(senha) < 6:
            return jsonify({'erro': 'Senha deve ter 6+ caracteres'}), 400

        if buscar_aluno_por_email(email):
            return jsonify({'erro': 'Email já cadastrado'}), 409

        novo_aluno = cadastrar_aluno(nome, email, senha)

        return jsonify({
            'mensagem': 'Cadastro realizado!',
            'aluno_id': novo_aluno.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()

        email = dados.get('email')
        senha = dados.get('senha')

        aluno = buscar_aluno_por_email(email)

        if not aluno or not aluno.check_senha(senha):
            return jsonify({'erro': 'Email ou senha inválidos'}), 401

        access_token = create_access_token(
            identity=str(aluno.id),
            expires_delta=timedelta(days=7)
        )

        return jsonify({
            'access_token': access_token,
            'aluno': {
                'id': aluno.id,
                'nome': aluno.nome_completo,
                'email': aluno.email
            }
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def perfil():
    try:
        aluno_id = int(get_jwt_identity())
        aluno = buscar_aluno_por_id(aluno_id)

        if not aluno:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        return jsonify(aluno.to_dict()), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
