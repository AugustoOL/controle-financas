from datetime import date

from flask import Blueprint, g, render_template, request

from app.models import Lancamento

from .auth import exigir_login

bp = Blueprint("dashboard", __name__)
bp.before_request(exigir_login)


def _ano_mes():
    hoje = date.today()
    try:
        ano = int(request.args.get("ano", hoje.year))
        mes = int(request.args.get("mes", hoje.month))
        if not (1 <= mes <= 12 and 1900 <= ano <= 2100):
            raise ValueError
    except ValueError:
        ano, mes = hoje.year, hoje.month
    return ano, mes


@bp.route("/")
def index():
    ano, mes = _ano_mes()
    lancamentos = Lancamento.do_mes(g.usuario.id, ano, mes)
    resumo = Lancamento.resumo(lancamentos)

    ant = (ano, mes - 1) if mes > 1 else (ano - 1, 12)
    prox = (ano, mes + 1) if mes < 12 else (ano + 1, 1)
    return render_template("dashboard.html", ano=ano, mes=mes, resumo=resumo,
                           recentes=lancamentos[:5], ant=ant, prox=prox)
