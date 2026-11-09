from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from app.models import Usuario
from app.models.categoria import ValidacaoError

bp = Blueprint("auth", __name__)


def exigir_login():
    """before_request dos blueprints protegidos. Sem usuário na sessão -> /login."""
    if g.usuario is None:
        session.clear()
        return redirect(url_for("auth.login"))


def _entrar(usuario):
    session.clear()  # evita fixação de sessão
    session["usuario_id"] = usuario.id


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(url_for("dashboard.index"))
    erros = {}
    if request.method == "POST":
        f = request.form
        try:
            usuario = Usuario.cadastrar(f.get("nome"), f.get("email"),
                                        f.get("senha"), f.get("confirmacao"))
            _entrar(usuario)
            flash("Conta criada com sucesso. Bem-vindo(a)!", "sucesso")
            return redirect(url_for("dashboard.index"))
        except ValidacaoError as e:
            erros = {e.campo: str(e)}
    return render_template("auth/cadastro.html", form=request.form, erros=erros)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("dashboard.index"))
    erros = {}
    if request.method == "POST":
        usuario = Usuario.autenticar(request.form.get("email"), request.form.get("senha"))
        if usuario:
            _entrar(usuario)
            return redirect(url_for("dashboard.index"))
        erros = {"senha": "E-mail ou senha incorretos.", "email": ""}
    return render_template("auth/login.html", form=request.form, erros=erros)


@bp.route("/sair", methods=["POST"])
def sair():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("auth.login"))
