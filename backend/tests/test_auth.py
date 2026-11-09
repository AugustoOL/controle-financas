import pytest

from app.models import Categoria, Lancamento, Usuario
from app.models.categoria import ValidacaoError
from conftest import SENHA

CADASTRO = {"nome": "Carla", "email": "carla@exemplo.com",
            "senha": SENHA, "confirmacao": SENHA}


def html(r):
    return r.get_data(as_text=True)


# ---------- cadastro ----------
def test_cadastro_ok_loga_e_cria_categorias_padrao(client, app):
    r = client.post("/cadastro", data=CADASTRO, follow_redirects=True)
    assert "Conta criada com sucesso" in html(r)
    assert "Resumo de" in html(r)
    with app.app_context():
        u = Usuario.query.filter_by(email="carla@exemplo.com").one()
        assert u.senha_hash != SENHA  # nunca senha pura
        assert Categoria.query.filter_by(usuario_id=u.id).count() == 7


def test_cadastro_email_duplicado_ignora_maiusculas(client, usuario):
    r = client.post("/cadastro", data={**CADASTRO, "email": "ANA@Exemplo.com"})
    assert "Já existe uma conta" in html(r)


def test_cadastro_email_guardado_em_minusculas(client, app):
    client.post("/cadastro", data={**CADASTRO, "email": "Carla@Exemplo.COM"})
    with app.app_context():
        assert Usuario.query.one().email == "carla@exemplo.com"


def test_cadastro_senha_curta(client, app):
    r = client.post("/cadastro", data={**CADASTRO, "senha": "123", "confirmacao": "123"})
    assert "no mínimo 6" in html(r)
    with app.app_context():
        assert Usuario.query.count() == 0


def test_cadastro_senhas_diferentes(client):
    r = client.post("/cadastro", data={**CADASTRO, "confirmacao": "outra-senha"})
    assert "não confere" in html(r)


@pytest.mark.parametrize("campo,valor,msg", [
    ("nome", "  ", "nome é obrigatório"),
    ("email", "sem-arroba", "e-mail válido"),
    ("email", "a@b", "e-mail válido"),
])
def test_cadastro_campos_invalidos(client, campo, valor, msg):
    r = client.post("/cadastro", data={**CADASTRO, campo: valor})
    assert msg in html(r)


def test_cadastro_erro_mantem_dados_digitados(client):
    r = client.post("/cadastro", data={**CADASTRO, "confirmacao": "x"})
    assert 'value="Carla"' in html(r) and 'value="carla@exemplo.com"' in html(r)


def test_modelo_valida_sem_http(ctx):
    with pytest.raises(ValidacaoError):
        Usuario.cadastrar("", "a@b.com", SENHA, SENHA)


# ---------- login / logout ----------
def test_login_ok(client, usuario):
    r = client.post("/login", data={"email": "ANA@exemplo.com", "senha": SENHA},
                    follow_redirects=True)
    assert "Resumo de" in html(r) and "Ana" in html(r)


def test_login_errado_mensagem_generica(client, usuario):
    r1 = client.post("/login", data={"email": "ana@exemplo.com", "senha": "errada"})
    r2 = client.post("/login", data={"email": "naoexiste@exemplo.com", "senha": "errada"})
    assert "E-mail ou senha incorretos." in html(r1)
    assert "E-mail ou senha incorretos." in html(r2)


@pytest.mark.parametrize("url", ["/", "/lancamentos/", "/lancamentos/novo",
                                 "/categorias/", "/categorias/nova"])
def test_rotas_protegidas_redirecionam_para_login(client, url):
    r = client.get(url)
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")
    r = client.get(url, follow_redirects=True)
    assert "Faça login para continuar." in html(r)


def test_posts_protegidos_sem_login(client, logado, app):
    r = client.post("/lancamentos/1/excluir")
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")


def test_logado_em_login_e_cadastro_vai_para_resumo(logado):
    for url in ("/login", "/cadastro"):
        r = logado.get(url)
        assert r.status_code == 302 and r.headers["Location"] == "/"


def test_logout_encerra_sessao(logado):
    r = logado.post("/sair", follow_redirects=True)
    assert "saiu da sua conta" in html(r)
    assert logado.get("/").status_code == 302


def test_logout_so_por_post(logado):
    assert logado.get("/sair").status_code == 405
    assert logado.get("/").status_code == 200  # continua logado


def test_menu_deslogado_esconde_areas_privadas(client):
    h = html(client.get("/login"))
    assert "Entrar" in h and "Criar conta" in h
    assert "Lançamentos" not in h and "Categorias" not in h


def test_menu_logado_mostra_nome_e_sair(logado):
    h = html(logado.get("/"))
    assert "Ana" in h and "Sair" in h and "Lançamentos" in h


def test_sessao_de_usuario_inexistente_e_rejeitada(app, client):
    with client.session_transaction() as s:
        s["usuario_id"] = 9999
    assert client.get("/").status_code == 302


def test_cookie_de_sessao_seguro(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


# ---------- isolamento entre usuários ----------
def _novo_lanc(app, uid, desc="Segredo da Ana"):
    with app.app_context():
        c = Categoria.query.filter_by(usuario_id=uid, nome="Lazer").one()
        return Lancamento.criar(uid, desc, "10", "2026-11-03", c.id).id


def test_usuario_b_nao_ve_dados_do_a(app, usuario, logado_b):
    _novo_lanc(app, 1)
    assert "Segredo da Ana" not in html(logado_b.get("/lancamentos/"))
    assert "Segredo da Ana" not in html(logado_b.get("/?ano=2026&mes=11"))


def test_usuario_b_nao_edita_nem_exclui_dados_do_a(app, usuario, logado_b):
    lid = _novo_lanc(app, 1)
    with app.app_context():
        cid = Categoria.query.filter_by(usuario_id=1, nome="Lazer").one().id
    assert logado_b.get(f"/lancamentos/{lid}/editar").status_code == 404
    r = logado_b.post(f"/lancamentos/{lid}/editar", data={
        "descricao": "Hack", "valor": "1", "data": "2026-11-03", "categoria_id": cid})
    assert r.status_code == 404
    assert logado_b.post(f"/lancamentos/{lid}/excluir").status_code == 404
    assert logado_b.get(f"/categorias/{cid}/editar").status_code == 404
    assert logado_b.post(f"/categorias/{cid}/excluir").status_code == 404
    with app.app_context():
        l = Lancamento.query.one()
        assert l.descricao == "Segredo da Ana"
        assert db_count_cat(cid) == 1


def db_count_cat(cid):
    return Categoria.query.filter_by(id=cid).count()


def test_lancamento_nao_aceita_categoria_de_outro_usuario(app, usuario, logado_b):
    with app.app_context():
        cid_a = Categoria.query.filter_by(usuario_id=1, nome="Lazer").one().id
    r = logado_b.post("/lancamentos/novo", data={
        "descricao": "X", "valor": "10", "data": "2026-11-03", "categoria_id": cid_a})
    assert "categoria válida" in html(r)
    with app.app_context():
        assert Lancamento.query.count() == 0


def test_categorias_separadas_por_usuario(app, logado, logado_b):
    logado.post("/categorias/nova", data={"nome": "Pets", "tipo": "despesa"})
    assert "Pets" in html(logado.get("/categorias/"))
    assert "Pets" not in html(logado_b.get("/categorias/"))
    # mesmo nome é permitido para outro usuário
    r = logado_b.post("/categorias/nova", data={"nome": "Pets", "tipo": "despesa"},
                      follow_redirects=True)
    assert "criada com sucesso" in html(r)
    with app.app_context():
        assert Categoria.query.filter_by(nome="Pets").count() == 2
