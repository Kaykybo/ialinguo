import re


class ValidacaoUtils:

    _EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def validar_email(self, email):
        return re.match(self._EMAIL_PATTERN, email) is not None

    def validar_senha(self, senha):
        return len(senha) >= 6

    def validar_nome(self, nome):
        return len(nome.strip()) >= 3
