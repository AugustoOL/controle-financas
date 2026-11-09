from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Categoria, Lancamento
from app.models.categoria import ValidacaoError

from .auth import exigir_login

bp = Blueprint("lancamentos", __name__, url_prefix="/lancamentos")
bp.before_request(exigir_login)


def _meu(id):
    """Lançamento do usuário logado; de outro usuário -> 404."""
    lanc = db.session.get(Lancamento, id)
    if lanc is None or lanc.usuario_id != g.usuario.id:
        abort(404)
    return lanc


def _categorias():
    return Categoria.query.filter_by(usuario_id=g.usuario.id).order_by(Categoria.tipo, Categoria.nome).all()


@bp.route("/")
def listar():
    tipo = request.args.get("tipo", "")
    categoria_id = request.args.get("categoria_id", type=int)
    busca = (request.args.get("q") or "").strip()

    q = Lancamento.query.join(Categoria).filter(Lancamento.usuario_id == g.usuario.id)
    if tipo in ("receita", "despesa"):
        q = q.filter(Categoria.tipo == tipo)
    if categoria_id:
        q = q.filter(Lancamento.categoria_id == categoria_id)
    if busca:
        q = q.filter(Lancamento.descricao.ilike(f"%{busca}%"))
    lancamentos = q.order_by(Lancamento.data.desc(), Lancamento.id.desc()).all()

    return render_template("lancamentos/lista.html", lancamentos=lancamentos,
                           categorias=_categorias(), tipo=tipo,
                           categoria_id=categoria_id, busca=busca)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        f = request.form
        try:
            Lancamento.criar(g.usuario.id, f.get("descricao"), f.get("valor"), f.get("data"),
                             f.get("categoria_id"), f.get("observacao"))
            flash("Lançamento registrado com sucesso.", "sucesso")
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
