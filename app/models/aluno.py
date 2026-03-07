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

    conversas = db.relationship('Conversa', backref='aluno', lazy=True, cascade='all, delete-orphan')
    questionarios = db.relationship('Questionario', backref='aluno', lazy=True, cascade='all, delete-orphan')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome_completo,
            'email': self.email,
            'nivel': self.nivel_ingles,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

    def __repr__(self):
        return f'<Aluno {self.email}>'
