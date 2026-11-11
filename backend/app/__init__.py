from pathlib import Path

from flask import Flask, g, request, session

from config import Config
from .extensions import db


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder=str(FRONTEND / "templates"),
                static_folder=str(FRONTEND / "static"))
    app.config.from_object(config_class)
    db.init_app(app)

    MESES = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
             "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    @app.template_filter("brl")
    def brl(valor):
        s = f"{valor:,.2f}"
        return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("moeda_input")
    def moeda_input(valor):
        """Valor para campo de formulário: 1.234,56 (sem 'R$')."""
        return brl(valor)[3:]

    @app.template_filter("data_br")
    def data_br(d):
        return d.strftime("%d/%m/%Y")

    app.jinja_env.globals["MESES"] = MESES

    def limites_data():
        from .models.lancamento import DATA_MIN, data_max
        return DATA_MIN.isoformat(), data_max().isoformat()

    app.jinja_env.globals["limites_data"] = limites_data

    @app.after_request
    def sem_cache_nas_telas(resposta):
        # Telas internas não ficam em cache: depois de "Sair", o botão Voltar
        # do navegador não mostra os dados da conta.
        if request.endpoint != "static":
            resposta.headers["Cache-Control"] = "no-store"
        return resposta

    @app.errorhandler(404)
    def nao_encontrado(_e):
        from flask import render_template
        return render_template("404.html"), 404

    @app.before_request
    def carregar_usuario():
        from .models import Usuario
        uid = session.get("usuario_id")
        g.usuario = db.session.get(Usuario, uid) if uid else None

    from .controllers.auth import bp as auth_bp
    from .controllers.dashboard import bp as dashboard_bp
    from .controllers.categorias import bp as categorias_bp
    from .controllers.lancamentos import bp as lancamentos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(lancamentos_bp)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
