from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import Aluno, Conversa, Mensagem, Feedback, Questionario
from app.ai_service import AIService
from app.utils import AudioUtils, ValidacaoUtils
from datetime import datetime, timedelta
import base64

api_bp = Blueprint('api', __name__)

# ========== HEALTH CHECK ==========

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200

# ========== ENDPOINTS DE AUTENTICAÇÃO ==========

@api_bp.route('/auth/cadastrar', methods=['POST'])
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
        
        if Aluno.query.filter_by(email=email).first():
            return jsonify({'erro': 'Email já cadastrado'}), 409
        
        novo_aluno = Aluno(
            nome_completo=nome,
            email=email
        )
        novo_aluno.set_senha(senha)
        
        db.session.add(novo_aluno)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Cadastro realizado!',
            'aluno_id': novo_aluno.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()
        
        email = dados.get('email')
        senha = dados.get('senha')
        
        aluno = Aluno.query.filter_by(email=email).first()
        
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

@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def perfil():
    try:
        user_id_str = get_jwt_identity()
        aluno_id = int(user_id_str)
        
        aluno = Aluno.query.get(aluno_id)
        
        if not aluno:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'id': aluno.id,
            'nome': aluno.nome_completo,
            'email': aluno.email,
            'nivel': aluno.nivel_ingles,
            'data_cadastro': aluno.data_cadastro.isoformat() if aluno.data_cadastro else None
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ========== ENDPOINTS DE CONTEXTOS ==========

@api_bp.route('/contextos', methods=['GET'])
@jwt_required()
def listar_contextos():
    """
    GET /api/contextos
    Lista todos os contextos disponíveis para conversa
    """
    contextos = []
    for k, v in AIService.CONTEXTOS.items():
        contextos.append({
            'id': k,
            'nome': k.replace('_', ' ').title(),
            'descricao': v[:100] + '...' if len(v) > 100 else v
        })
    
    return jsonify({'contextos': contextos}), 200

# ========== ENDPOINTS DE CONVERSA ==========

@api_bp.route('/conversas/iniciar', methods=['POST'])
@jwt_required()
def iniciar_conversa():
    """
    POST /api/conversas/iniciar
    Body: { "contexto": "string" } (opcional)
    """
    try:
        aluno_id = int(get_jwt_identity())
        dados = request.get_json() or {}
        
        contexto = dados.get('contexto', 'conversa livre')
        
        if contexto not in AIService.CONTEXTOS:
            contexto = 'conversa livre'
        
        nova_conversa = Conversa(
            aluno_id=aluno_id,
            contexto=contexto,
            status='ativa'
        )
        
        db.session.add(nova_conversa)
        db.session.commit()
        
        msg_inicial = f"Hello! I'm your AI assistant. Let's practice English in a {contexto} context. How can I help you today?"
        
        mensagem_ia = Mensagem(
            conversa_id=nova_conversa.id,
            remetente='ia',
            texto=msg_inicial
        )
        
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

@api_bp.route('/conversas/<int:conversa_id>/enviar', methods=['POST'])
@jwt_required()
def enviar_mensagem(conversa_id):
    """
    POST /api/conversas/<id>/enviar
    Body: { "mensagem": "string", "tipo": "texto" }
    """
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
        
        msg_aluno = Mensagem(
            conversa_id=conversa.id,
            remetente='aluno',
            texto=mensagem_texto,
            tipo=tipo
        )
        db.session.add(msg_aluno)
        
        historico = Mensagem.query.filter_by(conversa_id=conversa.id)\
            .order_by(Mensagem.timestamp.asc())\
            .limit(10)\
            .all()
        
        historico_lista = [
            {'remetente': m.remetente, 'texto': m.texto} 
            for m in historico
        ]
        
        resposta_ia = AIService.gerar_resposta(
            mensagem_aluno=mensagem_texto,
            contexto=conversa.contexto,
            historico=historico_lista
        )
        
        msg_ia = Mensagem(
            conversa_id=conversa.id,
            remetente='ia',
            texto=resposta_ia
        )
        db.session.add(msg_ia)
        
        db.session.commit()
        
        return jsonify({
            'resposta': resposta_ia,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@api_bp.route('/conversas/<int:conversa_id>/finalizar', methods=['POST'])
@jwt_required()
def finalizar_conversa(conversa_id):
    """
    POST /api/conversas/<id>/finalizar
    """
    try:
        aluno_id = int(get_jwt_identity())
        
        conversa = Conversa.query.filter_by(
            id=conversa_id, 
            aluno_id=aluno_id,
            status='ativa'
        ).first()
        
        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada'}), 404
        
        mensagens = Mensagem.query.filter_by(conversa_id=conversa.id)\
            .order_by(Mensagem.timestamp.asc())\
            .all()
        
        texto_conversa = "\n".join([
            f"{'Aluno' if m.remetente == 'aluno' else 'IA'}: {m.texto}"
            for m in mensagens
        ])
        
        feedback_data = AIService.gerar_feedback(texto_conversa, conversa.contexto)
        
        novo_feedback = Feedback(
            conversa_id=conversa.id,
            pontos_positivos=feedback_data.get('pontos_positivos', ''),
            pontos_melhoria=feedback_data.get('pontos_melhoria', ''),
            nota_fluencia=feedback_data.get('nota_fluencia', 5)
        )
        
        conversa.status = 'finalizada'
        conversa.data_fim = datetime.utcnow()
        
        db.session.add(novo_feedback)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Conversa finalizada com sucesso',
            'feedback': {
                'pontos_positivos': novo_feedback.pontos_positivos,
                'pontos_melhoria': novo_feedback.pontos_melhoria,
                'nota_fluencia': novo_feedback.nota_fluencia
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# ========== ENDPOINTS DE HISTÓRICO ==========

@api_bp.route('/historico/conversas', methods=['GET'])
@jwt_required()
def listar_historico_conversas():
    """
    GET /api/historico/conversas
    """
    try:
        aluno_id = int(get_jwt_identity())
        
        conversas = Conversa.query.filter_by(aluno_id=aluno_id)\
            .order_by(Conversa.data_inicio.desc())\
            .all()
        
        historico = []
        for c in conversas:
            feedback = Feedback.query.filter_by(conversa_id=c.id).first()
            
            historico.append({
                'conversa_id': c.id,
                'contexto': c.contexto,
                'data_inicio': c.data_inicio.isoformat(),
                'data_fim': c.data_fim.isoformat() if c.data_fim else None,
                'status': c.status,
                'feedback': {
                    'pontos_positivos': feedback.pontos_positivos if feedback else None,
                    'pontos_melhoria': feedback.pontos_melhoria if feedback else None,
                    'nota_fluencia': feedback.nota_fluencia if feedback else None
                } if feedback else None
            })
        
        return jsonify({'historico': historico}), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@api_bp.route('/historico/conversas/<int:conversa_id>', methods=['GET'])
@jwt_required()
def detalhes_conversa(conversa_id):
    """
    GET /api/historico/conversas/<id>
    """
    try:
        aluno_id = int(get_jwt_identity())
        
        conversa = Conversa.query.filter_by(
            id=conversa_id, 
            aluno_id=aluno_id
        ).first()
        
        if not conversa:
            return jsonify({'erro': 'Conversa não encontrada'}), 404
        
        mensagens = Mensagem.query.filter_by(conversa_id=conversa.id)\
            .order_by(Mensagem.timestamp.asc())\
            .all()
        
        feedback = Feedback.query.filter_by(conversa_id=conversa.id).first()
        
        return jsonify({
            'conversa': {
                'id': conversa.id,
                'contexto': conversa.contexto,
                'data_inicio': conversa.data_inicio.isoformat(),
                'data_fim': conversa.data_fim.isoformat() if conversa.data_fim else None,
                'status': conversa.status
            },
            'mensagens': [
                {
                    'remetente': m.remetente,
                    'texto': m.texto,
                    'tipo': m.tipo,
                    'timestamp': m.timestamp.isoformat()
                } for m in mensagens
            ],
            'feedback': {
                'pontos_positivos': feedback.pontos_positivos,
                'pontos_melhoria': feedback.pontos_melhoria,
                'nota_fluencia': feedback.nota_fluencia
            } if feedback else None
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ========== ENDPOINTS DE QUESTIONÁRIO ==========

@api_bp.route('/questionarios', methods=['POST'])
@jwt_required()
def salvar_questionario():
    """
    POST /api/questionarios
    Body: { "titulo": "string", "respostas": {} }
    """
    try:
        aluno_id = int(get_jwt_identity())
        dados = request.get_json()
        
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        titulo = dados.get('titulo', 'Questionário de Nivelamento')
        respostas = dados.get('respostas', {})
        
        novo_questionario = Questionario(
            aluno_id=aluno_id,
            titulo=titulo,
            respostas=respostas
        )
        
        db.session.add(novo_questionario)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Questionário salvo com sucesso',
            'questionario_id': novo_questionario.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@api_bp.route('/questionarios', methods=['GET'])
@jwt_required()
def listar_questionarios():
    """
    GET /api/questionarios
    """
    try:
        aluno_id = int(get_jwt_identity())
        
        questionarios = Questionario.query.filter_by(aluno_id=aluno_id)\
            .order_by(Questionario.data_preenchimento.desc())\
            .all()
        
        return jsonify({
            'questionarios': [
                {
                    'id': q.id,
                    'titulo': q.titulo,
                    'data': q.data_preenchimento.isoformat(),
                    'respostas': q.respostas
                } for q in questionarios
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500