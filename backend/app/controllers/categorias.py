from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Categoria
from app.models.categoria import ValidacaoError

from .auth import exigir_login

bp = Blueprint("categorias", __name__, url_prefix="/categorias")
bp.before_request(exigir_login)


def _minha(id):
    """Categoria do usuário logado; de outro usuário -> 404."""
    categoria = db.session.get(Categoria, id)
    if categoria is None or categoria.usuario_id != g.usuario.id:
        abort(404)
    return categoria


@bp.route("/")
def listar():
    tipo = request.args.get("tipo", "")
    q = Categoria.query.filter_by(usuario_id=g.usuario.id)
    if tipo in ("receita", "despesa"):
        q = q.filter_by(tipo=tipo)
    else:
        tipo = ""
    categorias = q.order_by(Categoria.tipo, Categoria.nome).all()
    return render_template("categorias/lista.html", categorias=categorias, tipo=tipo)


@bp.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        try:
            Categoria.criar(g.usuario.id, request.form.get("nome"), request.form.get("tipo"))
            flash("Categoria criada com sucesso.", "sucesso")
            return redirect(url_for("categorias.listar"))
        except ValidacaoError as e:
            flash(str(e), "erro")
    return render_template("categorias/form.html", categoria=None, form=request.form)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    categoria = _minha(id)
    if request.method == "POST":
        try:
            categoria.atualizar(request.form.get("nome"), request.form.get("tipo"))
            flash("Categoria atualizada.", "sucesso")
            return redirect(url_for("categorias.listar"))
        except ValidacaoError as e:
            flash(str(e), "erro")
    return render_template("categorias/form.html", categoria=categoria, form=request.form)


@bp.route("/<int:id>/excluir", methods=["POST"])
def excluir(id):
    categoria = _minha(id)
    try:
        categoria.excluir()
        flash("Categoria excluída.", "sucesso")
    except ValidacaoError as e:
        flash(str(e), "erro")
    return redirect(url_for("categorias.listar"))
