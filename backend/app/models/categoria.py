from app.extensions import db

TIPOS = ("receita", "despesa")


class ValidacaoError(ValueError):
    """Erro de regra de negócio/validação mostrado ao usuário."""


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    tipo = db.Column(db.String(10), nullable=False)  # receita | despesa

    lancamentos = db.relationship("Lancamento", back_populates="categoria")

    @staticmethod
    def validar(nome, tipo):
        nome = (nome or "").strip()
        if not nome:
            raise ValidacaoError("O nome da categoria é obrigatório.")
        if len(nome) > 50:
            raise ValidacaoError("O nome deve ter no máximo 50 caracteres.")
        if tipo not in TIPOS:
            raise ValidacaoError("Tipo inválido. Escolha receita ou despesa.")
        return nome

    @classmethod
    def criar(cls, nome, tipo):
        nome = cls.validar(nome, tipo)
        if cls.query.filter(db.func.lower(cls.nome) == nome.lower()).first():
            raise ValidacaoError("Já existe uma categoria com esse nome.")
        cat = cls(nome=nome, tipo=tipo)
        db.session.add(cat)
        db.session.commit()
        return cat

    def atualizar(self, nome, tipo):
        nome = self.validar(nome, tipo)
        outra = Categoria.query.filter(
            db.func.lower(Categoria.nome) == nome.lower(), Categoria.id != self.id
        ).first()
        if outra:
            raise ValidacaoError("Já existe uma categoria com esse nome.")
        if tipo != self.tipo and self.lancamentos:
            raise ValidacaoError(
                "Não é possível mudar o tipo de uma categoria que já tem lançamentos."
            )
        self.nome, self.tipo = nome, tipo
        db.session.commit()

    def excluir(self):
        if self.lancamentos:
            raise ValidacaoError(
                "Não é possível excluir: existem lançamentos nesta categoria."
            )
        db.session.delete(self)
        db.session.commit()
