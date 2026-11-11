import csv
import io
from datetime import date
from math import ceil

from flask import (Blueprint, Response, abort, flash, g, redirect, render_template,
                   request, url_for)

from app.extensions import db
from app.models import Categoria, Lancamento
from app.models.categoria import ValidacaoError

from .auth import exigir_login

bp = Blueprint("lancamentos", __name__, url_prefix="/lancamentos")
bp.before_request(exigir_login)

POR_PAGINA = 20


def _meu(id):
    """Lançamento do usuário logado; de outro usuário -> 404."""
    lanc = db.session.get(Lancamento, id)
    if lanc is None or lanc.usuario_id != g.usuario.id:
        abort(404)
    return lanc


def _categorias():
    return Categoria.query.filter_by(usuario_id=g.usuario.id).order_by(Categoria.tipo, Categoria.nome).all()


def _consulta(a):
    """Aplica os filtros da URL. Retorna (consulta, avisos, ordenar, ordem)."""
    ordenar = a.get("ordenar", "data")
    ordem = a.get("ordem", "desc")
    if ordenar not in Lancamento.ORDENACOES:
        ordenar = "data"
    if ordem not in ("asc", "desc"):
        ordem = "desc"
    q, avisos = Lancamento.consultar(
        g.usuario.id, tipo=a.get("tipo", ""), categoria_id=a.get("categoria_id", type=int),
        busca=a.get("q"), data_de=a.get("data_de"), data_ate=a.get("data_ate"),
        valor_min=a.get("valor_min"), valor_max=a.get("valor_max"),
        ordenar=ordenar, ordem=ordem)
    return q, avisos, ordenar, ordem


@bp.route("/")
def listar():
    a = request.args
    q, avisos, ordenar, ordem = _consulta(a)
    for aviso in avisos:
        flash(aviso, "erro")

    total = q.count()
    paginas = max(1, ceil(total / POR_PAGINA))
    pagina = min(max(a.get("pagina", 1, type=int) or 1, 1), paginas)
    itens = q.limit(POR_PAGINA).offset((pagina - 1) * POR_PAGINA).all()
    totais = Lancamento.resumo(q.all())  # soma de tudo o que está filtrado
    base = {k: v for k, v in a.items() if k != "pagina" and v}
    filtrando = (any(k not in ("ordenar", "ordem") for k in base)
                 or ordenar != "data" or ordem != "desc")
    avancado = any(a.get(k) for k in ("data_de", "data_ate", "valor_min", "valor_max")) \
        or ordenar != "data" or ordem != "desc"

    return render_template("lancamentos/lista.html", lancamentos=itens,
                           categorias=_categorias(), tipo=a.get("tipo", ""),
                           categoria_id=a.get("categoria_id", type=int),
                           busca=(a.get("q") or "").strip(), f=a,
                           ordenar=ordenar, ordem=ordem,
                           ordenacoes=Lancamento.ORDENACOES, total=total,
                           pagina=pagina, paginas=paginas, totais=totais, base=base,
                           filtrando=filtrando, avancado=avancado)


def _celula_csv(texto):
    """Evita que uma planilha trate o texto como fórmula (=, +, -, @)."""
    texto = str(texto or "")
    return "'" + texto if texto[:1] in ("=", "+", "-", "@", "\t", "\r") else texto


@bp.route("/exportar")
def exportar():
    """Baixa em CSV (abre no Excel) tudo o que está filtrado."""
    q, _avisos, _o, _d = _consulta(request.args)
    saida = io.StringIO()
    w = csv.writer(saida, delimiter=";")
    w.writerow(["Data", "Descrição", "Categoria", "Tipo", "Valor (R$)", "Observação"])
    for l in q.all():
        w.writerow([l.data.strftime("%d/%m/%Y"), _celula_csv(l.descricao),
                    _celula_csv(l.categoria.nome), l.tipo,
                    str(l.valor).replace(".", ","), _celula_csv(l.observacao)])
    return Response("\ufeff" + saida.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="lancamentos.csv"'})


@bp.route("/excluir-lote", methods=["POST"])
def excluir_lote():
    try:
        n = Lancamento.excluir_varios(g.usuario.id, request.form.getlist("ids"))
        flash("1 lançamento excluído." if n == 1 else f"{n} lançamentos excluídos.", "sucesso")
    except ValidacaoError as e:
        flash(str(e), "erro")
    return redirect(url_for("lancamentos.listar"))


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        f = request.form
        try:
            criados = Lancamento.criar_recorrente(
                g.usuario.id, f.get("descricao"), f.get("valor"), f.get("data"),
                f.get("categoria_id"), f.get("observacao"), f.get("repeticoes"))
            if len(criados) == 1:
                flash("Lançamento registrado com sucesso.", "sucesso")
            else:
                flash(f"{len(criados)} lançamentos registrados com sucesso (um por mês).", "sucesso")
            return redirect(url_for("lancamentos.listar"))
        except ValidacaoError as e:
            flash(str(e), "erro")
    return render_template("lancamentos/form.html", lancamento=None,
                           categorias=_categorias(), form=request.form,
                           hoje=date.today().isoformat())


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    lanc = _meu(id)
    if request.method == "POST":
        f = request.form
        try:
            lanc.atualizar(f.get("descricao"), f.get("valor"), f.get("data"),
                           f.get("categoria_id"), f.get("observacao"))
            flash("Lançamento atualizado.", "sucesso")
            return redirect(url_for("lancamentos.listar"))
        except ValidacaoError as e:
            db.session.rollback()
            flash(str(e), "erro")
    return render_template("lancamentos/form.html", lancamento=lanc,
                           categorias=_categorias(), form=request.form,
                           hoje=date.today().isoformat())


@bp.route("/<int:id>/excluir", methods=["POST"])
def excluir(id):
    lanc = _meu(id)
    lanc.excluir()
    flash("Lançamento excluído.", "sucesso")
    return redirect(url_for("lancamentos.listar"))
