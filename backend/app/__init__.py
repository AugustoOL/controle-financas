from pathlib import Path

from flask import Flask, g, session

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

    @app.template_filter("data_br")
    def data_br(d):
        return d.strftime("%d/%m/%Y")

    app.jinja_env.globals["MESES"] = MESES

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
