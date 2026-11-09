from app.models import Categoria, Lancamento


def cat_id(app, nome):
    with app.app_context():
        return Categoria.query.filter_by(nome=nome).one().id


def test_dashboard_abre(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Resumo de" in r.get_data(as_text=True)


def test_dashboard_mes_invalido_nao_quebra(client):
    assert client.get("/?mes=99&ano=abc").status_code == 200


def test_pagina_inexistente_retorna_404_amigavel(client):
    r = client.get("/lancamentos/9999/editar")
    assert r.status_code == 404
    assert "não encontrada" in r.get_data(as_text=True)


def test_fluxo_criar_lancamento(client, app):
    r = client.post("/lancamentos/novo", data={
        "descricao": "Mercado", "valor": "120,00", "data": "2026-11-03",
        "categoria_id": cat_id(app, "Alimentação"), "observacao": ""},
        follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "registrado com sucesso" in html
    assert "Mercado" in html
    with app.app_context():
        assert Lancamento.query.count() == 1


def test_lancamento_invalido_mostra_erro_e_mantem_dados(client, app):
    r = client.post("/lancamentos/novo", data={
        "descricao": "Mercado", "valor": "-5", "data": "2026-11-03",
        "categoria_id": cat_id(app, "Alimentação")})
    html = r.get_data(as_text=True)
    assert "maior que zero" in html
    assert 'value="Mercado"' in html  # não perde o que o usuário digitou
    with app.app_context():
        assert Lancamento.query.count() == 0


def test_editar_e_excluir_lancamento(client, app):
    cid = cat_id(app, "Lazer")
    client.post("/lancamentos/novo", data={
        "descricao": "Cinema", "valor": "30", "data": "2026-11-03", "categoria_id": cid})
    with app.app_context():
        lid = Lancamento.query.one().id
    r = client.post(f"/lancamentos/{lid}/editar", data={
        "descricao": "Teatro", "valor": "40", "data": "2026-11-03", "categoria_id": cid},
        follow_redirects=True)
    assert "Teatro" in r.get_data(as_text=True)
    r = client.post(f"/lancamentos/{lid}/excluir", follow_redirects=True)
    assert "excluído" in r.get_data(as_text=True)
    with app.app_context():
        assert Lancamento.query.count() == 0


def test_filtro_por_tipo(client, app):
    for desc, val, c in [("Salário X", "1000", "Salário"), ("Pizza", "50", "Alimentação")]:
        client.post("/lancamentos/novo", data={
            "descricao": desc, "valor": val, "data": "2026-11-03",
            "categoria_id": cat_id(app, c)})
    html = client.get("/lancamentos/?tipo=receita").get_data(as_text=True)
    assert "Salário X" in html and "Pizza" not in html


def test_busca_por_descricao(client, app):
    for desc in ("Pizza", "Cinema"):
        client.post("/lancamentos/novo", data={
            "descricao": desc, "valor": "10", "data": "2026-11-03",
            "categoria_id": cat_id(app, "Lazer")})
    html = client.get("/lancamentos/?q=piz").get_data(as_text=True)
    assert "Pizza" in html and "Cinema" not in html


def test_criar_categoria_e_bloquear_duplicada(client):
    r = client.post("/categorias/nova", data={"nome": "Pets", "tipo": "despesa"},
                    follow_redirects=True)
    assert "criada com sucesso" in r.get_data(as_text=True)
    r = client.post("/categorias/nova", data={"nome": "pets", "tipo": "despesa"})
    assert "Já existe" in r.get_data(as_text=True)


def test_excluir_categoria_com_lancamento_mostra_erro(client, app):
    cid = cat_id(app, "Lazer")
    client.post("/lancamentos/novo", data={
        "descricao": "Cinema", "valor": "30", "data": "2026-11-03", "categoria_id": cid})
    r = client.post(f"/categorias/{cid}/excluir", follow_redirects=True)
    assert "Não é possível excluir" in r.get_data(as_text=True)
