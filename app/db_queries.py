from app import db
from app.models import Aluno, Conversa, Mensagem, Feedback, Questionario


def buscar_aluno_por_email(email):
    return Aluno.query.filter_by(email=email).first()


def buscar_aluno_por_id(aluno_id):
    return Aluno.query.get(aluno_id)


def cadastrar_aluno(nome, email, senha):
    novo_aluno = Aluno(nome_completo=nome, email=email)
    novo_aluno.set_senha(senha)
    db.session.add(novo_aluno)
    db.session.commit()
    return novo_aluno


def iniciar_conversa(aluno_id, contexto):
    conversa = Conversa(aluno_id=aluno_id, contexto=contexto, status='ativa')
    db.session.add(conversa)
    db.session.commit()
    return conversa


def buscar_conversa_ativa(conversa_id, aluno_id):
    return Conversa.query.filter_by(
        id=conversa_id,
        aluno_id=aluno_id,
        status='ativa'
    ).first()


def buscar_conversa_por_id(conversa_id, aluno_id):
    return Conversa.query.filter_by(id=conversa_id, aluno_id=aluno_id).first()


def adicionar_mensagem(conversa_id, remetente, texto, tipo='texto'):
    mensagem = Mensagem(conversa_id=conversa_id, remetente=remetente, texto=texto, tipo=tipo)
    db.session.add(mensagem)
    db.session.commit()
    return mensagem


def criar_feedback(conversa_id, pontos_positivos, pontos_melhoria, nota_fluencia):
    feedback = Feedback(
        conversa_id=conversa_id,
        pontos_positivos=pontos_positivos,
        pontos_melhoria=pontos_melhoria,
        nota_fluencia=nota_fluencia
    )
    db.session.add(feedback)
    db.session.commit()
    return feedback


def finalizar_conversa(conversa):
    conversa.finalizar()
    db.session.commit()
    return conversa


def listar_conversas_aluno(aluno_id):
    return Conversa.query.filter_by(aluno_id=aluno_id, status='finalizada').order_by(Conversa.data_inicio.desc()).all()


def listar_mensagens_conversa(conversa_id):
    return Mensagem.query.filter_by(conversa_id=conversa_id).order_by(Mensagem.timestamp.asc()).all()


def buscar_feedback_conversa(conversa_id):
    return Feedback.query.filter_by(conversa_id=conversa_id).first()


def salvar_questionario(aluno_id, titulo, respostas):
    questionario = Questionario(aluno_id=aluno_id, titulo=titulo, respostas=respostas)
    db.session.add(questionario)
    db.session.commit()
    return questionario


def listar_questionarios_aluno(aluno_id):
    return Questionario.query.filter_by(aluno_id=aluno_id).order_by(Questionario.data_preenchimento.desc()).all()
