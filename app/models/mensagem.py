from app import db
from datetime import datetime


class Mensagem(db.Model):
    __tablename__ = 'mensagens'

    id = db.Column(db.Integer, primary_key=True)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversas.id'), nullable=False)
    remetente = db.Column(db.String(20), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(10), default='texto')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict_historico(self):
        return {'remetente': self.remetente, 'texto': self.texto}

    def to_dict(self):
        return {
            'remetente': self.remetente,
            'texto': self.texto,
            'tipo': self.tipo,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f'<Mensagem {self.id} - {self.remetente}>'
