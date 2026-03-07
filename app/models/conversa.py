from app import db
from datetime import datetime


class Conversa(db.Model):
    __tablename__ = 'conversas'

    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    contexto = db.Column(db.String(50), nullable=False, default='conversa livre')
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ativa')

    mensagens = db.relationship('Mensagem', backref='conversa', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='conversa', lazy=True, cascade='all, delete-orphan')

    def finalizar(self):
        self.status = 'finalizada'
        self.data_fim = datetime.utcnow()

    def get_historico_lista(self, limite=10):
        from app.models.mensagem import Mensagem
        mensagens = Mensagem.query.filter_by(conversa_id=self.id)\
            .order_by(Mensagem.timestamp.asc())\
            .limit(limite)\
            .all()
        return [m.to_dict_historico() for m in mensagens]

    def get_texto_completo(self):
        from app.models.mensagem import Mensagem
        mensagens = Mensagem.query.filter_by(conversa_id=self.id)\
            .order_by(Mensagem.timestamp.asc())\
            .all()
        return "\n".join([
            f"{'Aluno' if m.remetente == 'aluno' else 'IA'}: {m.texto}"
            for m in mensagens
        ])

    def to_dict(self):
        from app.models.feedback import Feedback
        feedback = Feedback.query.filter_by(conversa_id=self.id).first()
        return {
            'conversa_id': self.id,
            'contexto': self.contexto,
            'data_inicio': self.data_inicio.isoformat(),
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'status': self.status,
            'feedback': feedback.to_dict() if feedback else None
        }

    def __repr__(self):
        return f'<Conversa {self.id} - {self.contexto}>'
