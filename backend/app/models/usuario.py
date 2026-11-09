import re

from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from .categoria import Categoria, ValidacaoError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SENHA_MIN = 6

CATEGORIAS_PADRAO = [
    ("Salário", "receita"), ("Renda extra", "receita"),
    ("Alimentação", "despesa"), ("Moradia", "despesa"),
    ("Transporte", "despesa"), ("Lazer", "despesa"), ("Saúde", "despesa"),
]


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)  # sempre em minúsculas
    senha_hash = db.Column(db.String(255), nullable=False)

    categorias = db.relationship("Categoria", back_populates="usuario")
    lancamentos = db.relationship("Lancamento", back_populates="usuario")

    @staticmethod
    def validar(nome, email, senha, confirmacao):
        nome = (nome or "").strip()
        email = (email or "").strip().lower()
        senha = senha or ""
        if not nome:
            raise ValidacaoError("O nome é obrigatório.", "nome")
        if len(nome) > 80:
            raise ValidacaoError("O nome deve ter no máximo 80 caracteres.", "nome")
        if len(email) > 120 or not EMAIL_RE.match(email):
            raise ValidacaoError("Informe um e-mail válido.", "email")
        if len(senha) < SENHA_MIN:
            raise ValidacaoError(f"A senha deve ter no mínimo {SENHA_MIN} caracteres.", "senha")
        if senha != (confirmacao or ""):
            raise ValidacaoError("A confirmação de senha não confere.", "confirmacao")
        return nome, email, senha

    @classmethod
    def cadastrar(cls, nome, email, senha, confirmacao):
        nome, email, senha = cls.validar(nome, email, senha, confirmacao)
        if cls.query.filter_by(email=email).first():
            raise ValidacaoError("Já existe uma conta com esse e-mail.", "email")
        usuario = cls(nome=nome, email=email, senha_hash=generate_password_hash(senha))
        db.session.add(usuario)
        try:
            db.session.flush()
            for cat_nome, tipo in CATEGORIAS_PADRAO:
                db.session.add(Categoria(nome=cat_nome, tipo=tipo, usuario_id=usuario.id))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValidacaoError("Já existe uma conta com esse e-mail.", "email")
        return usuario

    @classmethod
    def autenticar(cls, email, senha):
        """Retorna o usuário se e-mail/senha conferem; senão, None."""
        usuario = cls.query.filter_by(email=(email or "").strip().lower()).first()
        if usuario and check_password_hash(usuario.senha_hash, senha or ""):
            return usuario
        return None
