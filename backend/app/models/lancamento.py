import re
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import extract

from app.extensions import db
from .categoria import Categoria, ValidacaoError

DATA_MIN = date(2000, 1, 1)
MAX_REPETICOES = 60

# Formatos de valor aceitos (ver Lancamento._interpretar_valor)
# re.ASCII: só os algarismos 0-9 valem (nada de dígitos de outros alfabetos)
_COM_VIRGULA = re.compile(r"-?(\d+|\d{1,3}(\.\d{3})+),\d{1,2}", re.ASCII)
_INTEIRO = re.compile(r"-?\d+", re.ASCII)
_MILHAR = re.compile(r"-?\d{1,3}(\.\d{3})+", re.ASCII)
_PONTO_DECIMAL = re.compile(r"-?\d+\.\d{1,2}", re.ASCII)


def data_max():
    """Última data aceita: 10 anos a partir de hoje."""
    return date.today() + timedelta(days=3650)


def somar_meses(d, n):
    """Mesmo dia daqui a n meses (dia 31 em mês curto vira o último dia)."""
    indice = d.month - 1 + n
    ano, mes = d.year + indice // 12, indice % 12 + 1
    return date(ano, mes, min(d.day, monthrange(ano, mes)[1]))


class Lancamento(db.Model):
    __tablename__ = "lancamento"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    observacao = db.Column(db.String(255))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    usuario = db.relationship("Usuario", back_populates="lancamentos")
    categoria = db.relationship("Categoria", back_populates="lancamentos")

    @property
    def tipo(self):
        return self.categoria.tipo

    # ---------- validação ----------
    @staticmethod
    def _interpretar_valor(texto):
        """Converte o texto digitado em Decimal com 2 casas.

        Aceita: `1.234,56` e `1234,56` (vírgula decimal, ponto de milhar),
        `1234`, `1.234` (milhar), `1234.56` e `10.5` (ponto decimal com 1-2 casas).
        Qualquer outra coisa (texto, `1e3`, `nan`, `0,001`) é recusada."""
        txt = str(texto if texto is not None else "").strip().replace(" ", "")
        if _COM_VIRGULA.fullmatch(txt):
            txt = txt.replace(".", "").replace(",", ".")
        elif _MILHAR.fullmatch(txt):
            txt = txt.replace(".", "")
        elif not (_INTEIRO.fullmatch(txt) or _PONTO_DECIMAL.fullmatch(txt)):
            raise ValidacaoError("Informe um valor numérico válido.")
        return Decimal(txt).quantize(Decimal("0.01"))

    @staticmethod
    def _interpretar_data(data):
        if isinstance(data, str):
            try:
                data = datetime.strptime(data, "%Y-%m-%d").date()
            except ValueError:
                raise ValidacaoError("Informe uma data válida.")
        if not isinstance(data, date):
            raise ValidacaoError("Informe uma data válida.")
        if not (DATA_MIN <= data <= data_max()):
            raise ValidacaoError(
                f"Informe uma data entre {DATA_MIN:%d/%m/%Y} e {data_max():%d/%m/%Y}.")
        return data

    @staticmethod
    def validar(usuario_id, descricao, valor, data, categoria_id):
        descricao = (descricao or "").strip()
        if not descricao:
            raise ValidacaoError("A descrição é obrigatória.")
        if len(descricao) > 100:
            raise ValidacaoError("A descrição deve ter no máximo 100 caracteres.")

        valor = Lancamento._interpretar_valor(valor)
        if valor <= 0:
            raise ValidacaoError("O valor deve ser maior que zero.")
        if valor > Decimal("99999999.99"):
            raise ValidacaoError("O valor informado é muito alto.")

        data = Lancamento._interpretar_data(data)

        try:
            categoria = db.session.get(Categoria, int(categoria_id))
        except (TypeError, ValueError):
            categoria = None
        if categoria is None or categoria.usuario_id != usuario_id:
            raise ValidacaoError("Selecione uma categoria válida.")

        return descricao, valor, data, categoria

    @staticmethod
    def validar_repeticoes(repeticoes):
        try:
            n = int(str(repeticoes or "1").strip())
        except ValueError:
            n = 0
        if not (1 <= n <= MAX_REPETICOES):
            raise ValidacaoError(f"Informe de 1 a {MAX_REPETICOES} meses para repetir.")
        return n

    # ---------- CRUD ----------
    @classmethod
    def criar(cls, usuario_id, descricao, valor, data, categoria_id, observacao=None):
        descricao, valor, data, categoria = cls.validar(
            usuario_id, descricao, valor, data, categoria_id)
        obs = (observacao or "").strip()[:255] or None
        lanc = cls(descricao=descricao, valor=valor, data=data,
                   categoria=categoria, observacao=obs, usuario_id=usuario_id)
        db.session.add(lanc)
        db.session.commit()
        return lanc

    @classmethod
    def criar_recorrente(cls, usuario_id, descricao, valor, data, categoria_id,
                         observacao=None, repeticoes=1):
        """Cria o lançamento e o repete todo mês, `repeticoes` vezes no total.

        Cada repetição é um lançamento independente ("Aluguel (2/12)"); tudo é
        validado antes de gravar, então ou grava todos ou nenhum."""
        n = cls.validar_repeticoes(repeticoes)
        descricao, valor, data, categoria = cls.validar(
            usuario_id, descricao, valor, data, categoria_id)
        obs = (observacao or "").strip()[:255] or None
        if n > 1 and len(descricao) + len(f" ({n}/{n})") > 100:
            raise ValidacaoError("A descrição é grande demais para repetir; encurte-a.")
        datas = [somar_meses(data, i) for i in range(n)]
        for d in datas:
            cls._interpretar_data(d)  # a última repetição também precisa ser válida
        criados = []
        for i, d in enumerate(datas):
            nome = descricao if n == 1 else f"{descricao} ({i + 1}/{n})"
            criados.append(cls(descricao=nome, valor=valor, data=d, categoria=categoria,
                               observacao=obs, usuario_id=usuario_id))
        db.session.add_all(criados)
        db.session.commit()
        return criados

    def atualizar(self, descricao, valor, data, categoria_id, observacao=None):
        descricao, valor, data, categoria = self.validar(
            self.usuario_id, descricao, valor, data, categoria_id)
        self.descricao, self.valor, self.data = descricao, valor, data
        self.categoria = categoria
        self.observacao = (observacao or "").strip()[:255] or None
        db.session.commit()

    def excluir(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def excluir_varios(cls, usuario_id, ids):
        """Exclui vários lançamentos do usuário de uma vez. Retorna quantos foram excluídos.

        Ids inválidos ou de outro usuário são ignorados."""
        validos = set()
        for i in ids or []:
            try:
                validos.add(int(i))
            except (TypeError, ValueError):
                continue
        if not validos:
            raise ValidacaoError("Selecione ao menos um lançamento.")
        n = (cls.query.filter(cls.usuario_id == usuario_id, cls.id.in_(validos))
             .delete(synchronize_session=False))
        db.session.commit()
        return n

    # ---------- consultas ----------
    @classmethod
    def do_mes(cls, usuario_id, ano, mes):
        return (cls.query
                .filter(cls.usuario_id == usuario_id,
                        extract("year", cls.data) == ano, extract("month", cls.data) == mes)
                .order_by(cls.data.desc(), cls.id.desc())
                .all())

    ORDENACOES = {"data": "data", "valor": "valor", "descricao": "descrição"}

    @classmethod
    def consultar(cls, usuario_id, tipo="", categoria_id=None, busca="",
                  data_de="", data_ate="", valor_min="", valor_max="",
                  ordenar="data", ordem="desc"):
        """Monta a consulta de lançamentos do usuário com filtros e ordenação.

        Retorna (consulta, avisos). Filtro inválido é ignorado e vira um aviso amigável
        em `avisos`; nunca lança exceção por causa de filtro. A consulta ainda não foi
        executada (quem chama pode contar, paginar ou exportar)."""
        avisos = []

        def _data(texto, nome):
            texto = (texto or "").strip()
            if not texto:
                return None
            try:
                return datetime.strptime(texto, "%Y-%m-%d").date()
            except ValueError:
                avisos.append(f"{nome} inválida: o filtro foi ignorado.")
                return None

        def _valor(texto, nome):
            texto = (texto or "").strip()
            if not texto:
                return None
            try:
                v = cls._interpretar_valor(texto)
                if v < 0:
                    raise ValidacaoError("negativo")
                return v
            except ValidacaoError:
                avisos.append(f"{nome} inválido: o filtro foi ignorado.")
                return None

        de, ate = _data(data_de, "Data inicial"), _data(data_ate, "Data final")
        if de and ate and de > ate:
            avisos.append("A data inicial é maior que a final: o filtro de data foi ignorado.")
            de = ate = None
        vmin, vmax = _valor(valor_min, "Valor mínimo"), _valor(valor_max, "Valor máximo")
        if vmin is not None and vmax is not None and vmin > vmax:
            avisos.append("O valor mínimo é maior que o máximo: o filtro de valor foi ignorado.")
            vmin = vmax = None

        q = cls.query.join(Categoria).filter(cls.usuario_id == usuario_id)
        if tipo in ("receita", "despesa"):
            q = q.filter(Categoria.tipo == tipo)
        if categoria_id:
            q = q.filter(cls.categoria_id == categoria_id)
        busca = (busca or "").strip()
        if busca:
            # % e _ digitados pela pessoa valem como texto comum, não como curinga
            seguro = busca.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            q = q.filter(cls.descricao.ilike(f"%{seguro}%", escape="\\"))
        if de:
            q = q.filter(cls.data >= de)
        if ate:
            q = q.filter(cls.data <= ate)
        if vmin is not None:
            q = q.filter(cls.valor >= vmin)
        if vmax is not None:
            q = q.filter(cls.valor <= vmax)

        coluna = {"data": cls.data, "valor": cls.valor,
                  "descricao": db.func.lower(cls.descricao)}.get(ordenar, cls.data)
        if ordem == "asc":
            q = q.order_by(coluna.asc(), cls.id.asc())
        else:
            q = q.order_by(coluna.desc(), cls.id.desc())
        return q, avisos

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
