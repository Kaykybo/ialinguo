from app import db
from datetime import datetime


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversas.id'), nullable=False)
    pontos_positivos = db.Column(db.Text, nullable=False)
    pontos_melhoria = db.Column(db.Text, nullable=False)
    nota_fluencia = db.Column(db.Integer)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'pontos_positivos': self.pontos_positivos,
            'pontos_melhoria': self.pontos_melhoria,
            'nota_fluencia': self.nota_fluencia
        }

    def __repr__(self):
        return f'<Feedback {self.id} - Conversa {self.conversa_id}>'
