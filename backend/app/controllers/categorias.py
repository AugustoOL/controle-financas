from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Categoria
from app.models.categoria import ValidacaoError

bp = Blueprint("categorias", __name__, url_prefix="/categorias")


@bp.route("/")
def listar():
    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()
    return render_template("categorias/lista.html", categorias=categorias)


@bp.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        try:
            Categoria.criar(request.form.get("nome"), request.form.get("tipo"))
            flash("Categoria criada com sucesso.", "sucesso")
            return redirect(url_for("categorias.listar"))
        except ValidacaoError as e:
            flash(str(e), "erro")
    return render_template("categorias/form.html", categoria=None, form=request.form)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    categoria = db.get_or_404(Categoria, id)
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
    categoria = db.get_or_404(Categoria, id)
    try:
        categoria.excluir()
        flash("Categoria excluída.", "sucesso")
    except ValidacaoError as e:
        flash(str(e), "erro")
    return redirect(url_for("categorias.listar"))
