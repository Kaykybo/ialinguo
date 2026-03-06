from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Aluno(UserMixin, db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    nivel_ingles = db.Column(db.String(20), default='iniciante')
    
    # Relacionamentos
    conversas = db.relationship('Conversa', backref='aluno', lazy=True, cascade='all, delete-orphan')
    questionarios = db.relationship('Questionario', backref='aluno', lazy=True, cascade='all, delete-orphan')
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Aluno {self.email}>'

class Conversa(db.Model):
    __tablename__ = 'conversas'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    contexto = db.Column(db.String(50), nullable=False, default='conversa livre')
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ativa')
    
    # Relacionamentos
    mensagens = db.relationship('Mensagem', backref='conversa', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='conversa', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conversa {self.id} - {self.contexto}>'

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    
    id = db.Column(db.Integer, primary_key=True)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversas.id'), nullable=False)
    remetente = db.Column(db.String(20), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(10), default='texto')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Mensagem {self.id} - {self.remetente}>'

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversas.id'), nullable=False)
    pontos_positivos = db.Column(db.Text, nullable=False)
    pontos_melhoria = db.Column(db.Text, nullable=False)
    nota_fluencia = db.Column(db.Integer)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.id} - Conversa {self.conversa_id}>'

class Questionario(db.Model):
    __tablename__ = 'questionarios'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    respostas = db.Column(db.JSON, nullable=False)
    data_preenchimento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Questionario {self.id} - {self.titulo}>'