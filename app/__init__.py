from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ialingo-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ialingo.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'ialingo-jwt-secret-key-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 604800  # 7 dias em segundos
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'  # Forçar claim padrão
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'msg'  # Mensagens de erro
    
    # Inicializar extensões
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # ===== CORREÇÃO CRÍTICA =====
    # Adicionar callback para garantir que identity é string
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)  # Garante que sempre retorna string
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return Aluno.query.get(int(identity))
    # =============================
    
    # Registrar rotas da API
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Importar modelos para o lookup funcionar
    from app.models import Aluno
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    return app