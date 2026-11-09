from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import extract

from app.extensions import db
from .categoria import Categoria, ValidacaoError


class Lancamento(db.Model):
    __tablename__ = "lancamento"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    observacao = db.Column(db.String(255))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

    categoria = db.relationship("Categoria", back_populates="lancamentos")

    @property
    def tipo(self):
        return self.categoria.tipo

    # ---------- validação ----------
    @staticmethod
    def validar(descricao, valor, data, categoria_id):
        descricao = (descricao or "").strip()
        if not descricao:
            raise ValidacaoError("A descrição é obrigatória.")
        if len(descricao) > 100:
            raise ValidacaoError("A descrição deve ter no máximo 100 caracteres.")

        try:
            valor = Decimal(str(valor).replace(",", ".").strip())
        except (InvalidOperation, AttributeError):
            raise ValidacaoError("Informe um valor numérico válido.")
        if not valor.is_finite() or valor <= 0:
            raise ValidacaoError("O valor deve ser maior que zero.")
        if valor > Decimal("99999999.99"):
            raise ValidacaoError("O valor informado é muito alto.")
        valor = valor.quantize(Decimal("0.01"))

        if isinstance(data, str):
            try:
                data = datetime.strptime(data, "%Y-%m-%d").date()
            except ValueError:
                raise ValidacaoError("Informe uma data válida.")
        if not isinstance(data, date):
            raise ValidacaoError("Informe uma data válida.")

        try:
            categoria = db.session.get(Categoria, int(categoria_id))
        except (TypeError, ValueError):
            categoria = None
        if categoria is None:
            raise ValidacaoError("Selecione uma categoria válida.")

        return descricao, valor, data, categoria

    # ---------- CRUD ----------
    @classmethod
    def criar(cls, descricao, valor, data, categoria_id, observacao=None):
        descricao, valor, data, categoria = cls.validar(descricao, valor, data, categoria_id)
        obs = (observacao or "").strip()[:255] or None
        lanc = cls(descricao=descricao, valor=valor, data=data,
                   categoria=categoria, observacao=obs)
        db.session.add(lanc)
        db.session.commit()
        return lanc

    def atualizar(self, descricao, valor, data, categoria_id, observacao=None):
        descricao, valor, data, categoria = self.validar(descricao, valor, data, categoria_id)
        self.descricao, self.valor, self.data = descricao, valor, data
        self.categoria = categoria
        self.observacao = (observacao or "").strip()[:255] or None
        db.session.commit()

    def excluir(self):
        db.session.delete(self)
        db.session.commit()

    # ---------- consultas ----------
    @classmethod
    def do_mes(cls, ano, mes):
        return (cls.query
                .filter(extract("year", cls.data) == ano, extract("month", cls.data) == mes)
                .order_by(cls.data.desc(), cls.id.desc())
                .all())

    @staticmethod
    def resumo(lancamentos):
        """Totais de receitas, despesas, saldo e total por categoria."""
        receitas = Decimal("0.00")
        despesas = Decimal("0.00")
        por_categoria = {}
        for l in lancamentos:
            if l.tipo == "receita":
                receitas += l.valor
            else:
                despesas += l.valor
            chave = (l.categoria.nome, l.tipo)
            por_categoria[chave] = por_categoria.get(chave, Decimal("0.00")) + l.valor
        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": receitas - despesas,
            "por_categoria": sorted(
                [{"nome": n, "tipo": t, "total": v} for (n, t), v in por_categoria.items()],
                key=lambda x: x["total"], reverse=True),
        }
