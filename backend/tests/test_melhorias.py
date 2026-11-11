import re
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.models import Categoria, Lancamento, Usuario
from app.models.categoria import ValidacaoError
from app.models.lancamento import somar_meses


def html(r):
    return r.get_data(as_text=True)


def cat(app, nome, uid=1):
    with app.app_context():
        return Categoria.query.filter_by(usuario_id=uid, nome=nome).one().id


# ---------- parser de valor ----------
@pytest.mark.parametrize("texto,esperado", [
    ("1.234,56", "1234.56"), ("2.000,00", "2000.00"), ("1234,56", "1234.56"),
    ("1234.56", "1234.56"), ("0,01", "0.01"), ("10", "10.00"), ("10,5", "10.50"),
    ("1.000.000,00", "1000000.00"),
    ("1.234", "1234.00"),  # ponto com 3 casas = milhar, nunca R$ 1,23
    ("12.345", "12345.00"),
])
def test_valor_aceito(ctx, usuario, texto, esperado):
    l = Lancamento.criar(usuario, "X", texto, "2026-11-03", cat_id(usuario))
    assert l.valor == Decimal(esperado)


def cat_id(uid):
    return Categoria.query.filter_by(usuario_id=uid, nome="Lazer").one().id


@pytest.mark.parametrize("texto", [
    "abc", "-5", "-1.234,56", "1.2.3,5", "12,3a", "0,001", "1,2,3", "R$ 5", "1e3", "1E3",
    "nan", "inf", "0", "0,00", "", None, "1,234", "--5", "١٢٣"])
def test_valor_recusado(ctx, usuario, texto):
    with pytest.raises(ValidacaoError):
        Lancamento.criar(usuario, "X", texto, "2026-11-03", cat_id(usuario))
    assert Lancamento.query.count() == 0


def test_edicao_mostra_valor_com_virgula(logado, app):
    logado.post("/lancamentos/novo", data={"descricao": "Mercado", "valor": "150,50",
                                           "data": "2026-11-06", "categoria_id": cat(app, "Alimentação")})
    with app.app_context():
        lid = Lancamento.query.one().id
    h = html(logado.get(f"/lancamentos/{lid}/editar"))
    assert 'value="150,50"' in h and "150.50" not in h


# ---------- datas ----------
@pytest.mark.parametrize("d", ["0001-01-01", "1999-12-31", "2999-01-01"])
def test_data_fora_do_intervalo(ctx, usuario, d):
    with pytest.raises(ValidacaoError):
        Lancamento.criar(usuario, "X", "10", d, cat_id(usuario))


def test_data_limites_aceitos(ctx, usuario):
    Lancamento.criar(usuario, "Antiga", "10", "2000-01-01", cat_id(usuario))
    Lancamento.criar(usuario, "Futura", "10", date.today() + timedelta(days=365), cat_id(usuario))


def test_formulario_limita_data_no_navegador(logado):
    h = html(logado.get("/lancamentos/novo"))
    assert 'min="2000-01-01"' in h and "max=" in h


# ---------- senha ----------
def test_cadastro_recusa_senha_so_de_espacos(client, app):
    r = client.post("/cadastro", data={"nome": "A", "email": "a@x.com",
                                       "senha": "      ", "confirmacao": "      "})
    assert "apenas espaços" in html(r)
    with app.app_context():
        assert Usuario.query.count() == 0


def test_senha_com_espaco_no_meio_continua_valida(client):
    r = client.post("/cadastro", data={"nome": "A", "email": "a@x.com",
                                       "senha": "minha senha", "confirmacao": "minha senha"})
    assert r.status_code == 302


# ---------- cache ----------
def test_telas_nao_ficam_em_cache(logado, client):
    assert logado.get("/").headers["Cache-Control"] == "no-store"
    assert logado.get("/lancamentos/").headers["Cache-Control"] == "no-store"
    assert client.get("/login").headers["Cache-Control"] == "no-store"
    assert "no-store" not in logado.get("/static/style.css").headers.get("Cache-Control", "")


# ---------- busca com curingas ----------
def test_busca_trata_percent_e_underline_como_texto(logado, app):
    for desc in ("Pizza", "Desconto 10%", "nota_fiscal"):
        logado.post("/lancamentos/novo", data={"descricao": desc, "valor": "10", "data": "2026-11-03",
                                               "categoria_id": cat(app, "Lazer")})
    h = html(logado.get("/lancamentos/?q=%25"))
    assert "Desconto 10%" in h and "Pizza" not in h and "nota_fiscal" not in h
    h = html(logado.get("/lancamentos/?q=_"))
    assert "nota_fiscal" in h and "Pizza" not in h and "Desconto" not in h


# ---------- paginação e total ----------
@pytest.fixture
def muitos(app, usuario):
    with app.app_context():
        c = cat_id(usuario)
        r = Categoria.query.filter_by(usuario_id=usuario, nome="Salário").one().id
        for i in range(45):
            Lancamento.criar(usuario, f"Gasto {i:02d}", "10", date(2026, 11, 1) + timedelta(days=i % 28), c)
        Lancamento.criar(usuario, "Salário grande", "1000", "2026-11-05", r)


def test_paginacao(logado, muitos):
    p1 = html(logado.get("/lancamentos/?ordenar=descricao&ordem=asc"))
    assert "Página 1 de 3" in p1 and p1.count('name="ids"') == 20
    p3 = html(logado.get("/lancamentos/?ordenar=descricao&ordem=asc&pagina=3"))
    assert "Página 3 de 3" in p3 and p3.count('name="ids"') == 6
    assert "pagina=2" in p1  # link da próxima página mantém os filtros


def test_pagina_invalida_nao_quebra(logado, muitos):
    for p in ("0", "-3", "abc", "999"):
        assert logado.get(f"/lancamentos/?pagina={p}").status_code == 200


def test_total_considera_todos_os_filtrados_e_nao_so_a_pagina(logado, muitos):
    h = html(logado.get("/lancamentos/?tipo=despesa"))
    assert "<strong>45</strong> lançamentos" in h
    assert "R$ 450,00" in h  # 45 x 10, mesmo com 20 por página


def test_total_com_um_so_item_usa_singular(logado, muitos):
    h = html(logado.get("/lancamentos/?q=grande"))
    assert re.search(r"<strong>1</strong> lançamento\s", h)


# ---------- exportar CSV ----------
def test_exporta_csv_com_filtros(logado, app):
    for d, v, c in [("Mercado", "150,50", "Alimentação"), ("Cinema", "30", "Lazer")]:
        logado.post("/lancamentos/novo", data={"descricao": d, "valor": v, "data": "2026-11-03",
                                               "categoria_id": cat(app, c)})
    r = logado.get("/lancamentos/exportar?q=merc")
    assert r.status_code == 200 and r.mimetype == "text/csv"
    assert "attachment" in r.headers["Content-Disposition"]
    texto = r.get_data(as_text=True)
    assert texto.startswith("﻿") and "Data;Descrição;Categoria" in texto
    assert "03/11/2026;Mercado;Alimentação;despesa;150,50" in texto and "Cinema" not in texto


def test_csv_neutraliza_formulas(logado, app):
    logado.post("/lancamentos/novo", data={"descricao": "=SOMA(A1)", "valor": "10", "data": "2026-11-03",
                                           "categoria_id": cat(app, "Lazer")})
    assert "'=SOMA(A1)" in logado.get("/lancamentos/exportar").get_data(as_text=True)


def test_csv_exige_login_e_isola_usuarios(client, app, usuario, logado_b):
    with app.app_context():
        Lancamento.criar(usuario, "Segredo", "10", "2026-11-03", cat_id(usuario))
    assert client.get("/lancamentos/exportar").status_code == 302
    assert "Segredo" not in logado_b.get("/lancamentos/exportar").get_data(as_text=True)


# ---------- lançamento recorrente ----------
def test_somar_meses_ajusta_fim_de_mes():
    assert somar_meses(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert somar_meses(date(2026, 1, 31), 2) == date(2026, 3, 31)
    assert somar_meses(date(2026, 11, 15), 3) == date(2027, 2, 15)
    assert somar_meses(date(2024, 1, 31), 1) == date(2024, 2, 29)


def test_recorrente_cria_um_por_mes(ctx, usuario):
    lista = Lancamento.criar_recorrente(usuario, "Aluguel", "1.500,00", "2026-11-05", cat_id(usuario), "PIX", 3)
    assert [l.data for l in lista] == [date(2026, 11, 5), date(2026, 12, 5), date(2027, 1, 5)]
    assert [l.descricao for l in lista] == ["Aluguel (1/3)", "Aluguel (2/3)", "Aluguel (3/3)"]
    assert all(l.valor == Decimal("1500.00") and l.observacao == "PIX" for l in lista)


def test_recorrente_com_1_mes_nao_muda_nada(ctx, usuario):
    (l,) = Lancamento.criar_recorrente(usuario, "Aluguel", "10", "2026-11-05", cat_id(usuario), None, "1")
    assert l.descricao == "Aluguel"


@pytest.mark.parametrize("n", ["0", "61", "-1", "abc", "1.5"])
def test_recorrente_recusa_quantidade_invalida(ctx, usuario, n):
    with pytest.raises(ValidacaoError):
        Lancamento.criar_recorrente(usuario, "X", "10", "2026-11-05", cat_id(usuario), None, n)
    assert Lancamento.query.count() == 0


def test_recorrente_ou_grava_tudo_ou_nada(ctx, usuario):
    # a repetição passaria do limite de datas: nenhuma deve ser gravada
    inicio = date.today() + timedelta(days=3600)
    with pytest.raises(ValidacaoError):
        Lancamento.criar_recorrente(usuario, "X", "10", inicio, cat_id(usuario), None, 12)
    assert Lancamento.query.count() == 0


def test_recorrente_descricao_longa_demais(ctx, usuario):
    with pytest.raises(ValidacaoError):
        Lancamento.criar_recorrente(usuario, "x" * 99, "10", "2026-11-05", cat_id(usuario), None, 12)


def test_formulario_recorrente_pela_tela(logado, app):
    r = logado.post("/lancamentos/novo", data={
        "descricao": "Internet", "valor": "99,90", "data": "2026-11-10",
        "categoria_id": cat(app, "Moradia"), "repeticoes": "4"}, follow_redirects=True)
    assert "4 lançamentos registrados com sucesso" in html(r)
    with app.app_context():
        assert Lancamento.query.count() == 4


def test_edicao_nao_oferece_recorrencia(logado, app):
    logado.post("/lancamentos/novo", data={"descricao": "X", "valor": "10", "data": "2026-11-10",
                                           "categoria_id": cat(app, "Lazer")})
    with app.app_context():
        lid = Lancamento.query.one().id
    assert "repeticoes" not in html(logado.get(f"/lancamentos/{lid}/editar"))
    assert "repeticoes" in html(logado.get("/lancamentos/novo"))


def test_recorrente_usa_categoria_do_proprio_usuario(app, usuario, logado_b):
    r = logado_b.post("/lancamentos/novo", data={
        "descricao": "X", "valor": "10", "data": "2026-11-10",
        "categoria_id": cat(app, "Lazer", 1), "repeticoes": "3"})
    assert "categoria válida" in html(r)
    with app.app_context():
        assert Lancamento.query.count() == 0


# ---------- ações em lote ----------
@pytest.fixture
def tres(app, usuario):
    with app.app_context():
        return [Lancamento.criar(usuario, n, "10", "2026-11-03", cat_id(usuario)).id
                for n in ("A", "B", "C")]


def test_exclui_varios_de_uma_vez(logado, app, tres):
    r = logado.post("/lancamentos/excluir-lote", data={"ids": tres[:2]}, follow_redirects=True)
    assert "2 lançamentos excluídos" in html(r)
    with app.app_context():
        assert [l.descricao for l in Lancamento.query.all()] == ["C"]


def test_lote_com_um_item_usa_singular(logado, tres):
    r = logado.post("/lancamentos/excluir-lote", data={"ids": tres[0]}, follow_redirects=True)
    assert "1 lançamento excluído." in html(r)


def test_lote_sem_selecao_avisa(logado, app, tres):
    r = logado.post("/lancamentos/excluir-lote", data={}, follow_redirects=True)
    assert "Selecione ao menos um lançamento" in html(r)
    with app.app_context():
        assert Lancamento.query.count() == 3


def test_lote_ignora_ids_invalidos(logado, app, tres):
    r = logado.post("/lancamentos/excluir-lote", data={"ids": ["abc", "", str(tres[0])]},
                    follow_redirects=True)
    assert "1 lançamento excluído." in html(r)


def test_lote_nao_apaga_dados_de_outro_usuario(app, tres, logado_b):
    r = logado_b.post("/lancamentos/excluir-lote", data={"ids": tres}, follow_redirects=True)
    assert "0 lançamentos excluídos" in html(r)
    with app.app_context():
        assert Lancamento.query.count() == 3


def test_lote_so_por_post_e_com_login(client, logado, tres):
    assert logado.get("/lancamentos/excluir-lote").status_code == 405
    r = client.post("/lancamentos/excluir-lote", data={"ids": tres})
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")


def test_lista_tem_caixas_de_selecao_e_botao_de_lote(logado, tres):
    h = html(logado.get("/lancamentos/"))
    assert h.count('name="ids"') == 3
    assert "Excluir selecionados" in h and "Exportar CSV" in h
