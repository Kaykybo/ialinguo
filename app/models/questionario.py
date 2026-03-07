from app import db
from datetime import datetime


class Questionario(db.Model):
    __tablename__ = 'questionarios'

    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    respostas = db.Column(db.JSON, nullable=False)
    data_preenchimento = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'data': self.data_preenchimento.isoformat(),
            'respostas': self.respostas
        }

    def __repr__(self):
        return f'<Questionario {self.id} - {self.titulo}>'
