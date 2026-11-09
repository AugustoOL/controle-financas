import pytest

from app import create_app
from app.extensions import db
from app.models import Usuario
from config import TestConfig

SENHA = "segredo123"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente sem login."""
    return app.test_client()


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


def _criar_usuario(app, nome, email):
    with app.app_context():
        return Usuario.cadastrar(nome, email, SENHA, SENHA).id


@pytest.fixture
def usuario(app):
    """Id do usuário A (com as categorias padrão)."""
    return _criar_usuario(app, "Ana", "ana@exemplo.com")


@pytest.fixture
def usuario_b(app):
    return _criar_usuario(app, "Bruno", "bruno@exemplo.com")


def _logar(app, email):
    c = app.test_client()
    r = c.post("/login", data={"email": email, "senha": SENHA})
    assert r.status_code == 302
    return c


@pytest.fixture
def logado(app, usuario):
    """Cliente logado como o usuário A."""
    return _logar(app, "ana@exemplo.com")


@pytest.fixture
def logado_b(app, usuario_b):
    return _logar(app, "bruno@exemplo.com")
