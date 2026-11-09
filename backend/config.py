import os
from pathlib import Path

# O arquivo do banco SQLite fica na pasta database/ na raiz do projeto
DB_PATH = Path(__file__).resolve().parents[1] / "database" / "financas.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-troque-em-producao")
    # Local: SQLite. Em hospedagem, defina DATABASE_URL (PostgreSQL).
    _db = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")
    # Alguns provedores entregam "postgres://", o SQLAlchemy exige "postgresql://"
    SQLALCHEMY_DATABASE_URI = _db.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "teste"
