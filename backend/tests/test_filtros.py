from datetime import date

import pytest

from app.models import Categoria, Lancamento


def html(r):
    return r.get_data(as_text=True)


def cid(app, nome, uid=1):
    with app.app_context():
        return Categoria.query.filter_by(usuario_id=uid, nome=nome).one().id


@pytest.fixture
def dados(app, usuario):
    """Lançamentos do usuário A com datas, valores e descrições variados."""
    with app.app_context():
        c = {n: Categoria.query.filter_by(usuario_id=usuario, nome=n).one().id
             for n in ("Salário", "Lazer", "Alimentação")}
        Lancamento.criar(usuario, "Salário mensal", "3000", date(2026, 11, 5), c["Salário"])
        Lancamento.criar(usuario, "Pizza", "50", date(2026, 11, 10), c["Alimentação"])
        Lancamento.criar(usuario, "Cinema", "30,50", date(2026, 10, 20), c["Lazer"])
        Lancamento.criar(usuario, "Aluguel de barco", "1.200,00", date(2026, 9, 1), c["Lazer"])


def ordem_na_tela(texto, *nomes):
    return sorted(nomes, key=texto.index)


# ---------- máscara / formulário ----------
def test_form_novo_tem_mascara_rotulo_e_ajuda_da_data(logado):
    h = html(logado.get("/lancamentos/novo"))
    assert "data-mascara-valor" in h
    assert "Data da compra ou do recebimento" in h
    assert "Informe o dia em que o gasto ou o recebimento aconteceu." in h
    assert 'aria-describedby="data-ajuda"' in h and 'id="data-ajuda"' in h
    assert "app.js" in h


def test_edicao_preenche_valor_formatado(logado, app, dados):
    with app.app_context():
        lid = Lancamento.query.filter_by(descricao="Aluguel de barco").one().id
    assert 'value="1.200,00"' in html(logado.get(f"/lancamentos/{lid}/editar"))


def test_post_com_valor_mascarado(logado, app):
    logado.post("/lancamentos/novo", data={
        "descricao": "TV", "valor": "1.234,56", "data": "2026-11-03",
        "categoria_id": cid(app, "Lazer")})
    with app.app_context():
        assert str(Lancamento.query.one().valor) == "1234.56"


# ---------- filtros de lançamentos ----------
def test_filtro_por_data(logado, dados):
    h = html(logado.get("/lancamentos/?data_de=2026-10-01&data_ate=2026-11-06"))
    assert "Salário mensal" in h and "Cinema" in h
    assert "Pizza" not in h and "Aluguel de barco" not in h


def test_filtro_por_valor(logado, dados):
    h = html(logado.get("/lancamentos/?valor_min=40&valor_max=1.500,00"))
    assert "Pizza" in h and "Aluguel de barco" in h
    assert "Cinema" not in h and "Salário mensal" not in h


@pytest.mark.parametrize("qs,primeiro,ultimo", [
    ("ordenar=valor&ordem=asc", "Cinema", "Salário mensal"),
    ("ordenar=valor&ordem=desc", "Salário mensal", "Cinema"),
    ("ordenar=descricao&ordem=asc", "Aluguel de barco", "Salário mensal"),
    ("ordenar=data&ordem=asc", "Aluguel de barco", "Pizza"),
    ("ordenar=data&ordem=desc", "Pizza", "Aluguel de barco"),
])
def test_ordenacao(logado, dados, qs, primeiro, ultimo):
    h = html(logado.get(f"/lancamentos/?{qs}"))
    nomes = ordem_na_tela(h, "Aluguel de barco", "Cinema", "Pizza", "Salário mensal")
    assert nomes[0] == primeiro and nomes[-1] == ultimo


def test_filtros_combinados_com_existentes(logado, app, dados):
    h = html(logado.get(f"/lancamentos/?tipo=despesa&categoria_id={cid(app, 'Lazer')}"
                        "&q=cin&valor_max=100"))
    assert "Cinema" in h and "Pizza" not in h and "Aluguel" not in h


@pytest.mark.parametrize("qs,aviso", [
    ("data_de=31/02/2026", "Data inicial inválida"),
    ("data_ate=ontem", "Data final inválida"),
    ("valor_min=abc", "Valor mínimo inválido"),
    ("valor_max=-5", "Valor máximo inválido"),
    ("data_de=2026-12-01&data_ate=2026-01-01", "data inicial é maior"),
    ("valor_min=500&valor_max=10", "valor mínimo é maior"),
])
def test_filtro_invalido_e_ignorado_com_aviso(logado, dados, qs, aviso):
    r = logado.get(f"/lancamentos/?{qs}")
    assert r.status_code == 200
    h = html(r)
    assert aviso in h
    assert "Pizza" in h and "Cinema" in h  # nada foi filtrado


def test_ordenacao_invalida_nao_quebra(logado, dados):
    r = logado.get("/lancamentos/?ordenar=senha_hash&ordem=xx")
    assert r.status_code == 200 and "Pizza" in html(r)


def test_filtros_nao_vazam_dados_de_outro_usuario(app, dados, logado_b):
    # logado_b é o usuário B; os dados são do A
    with app.app_context():
        from app.models import Usuario
        b = Usuario.query.filter_by(email="bruno@exemplo.com").one().id
        c = Categoria.query.filter_by(usuario_id=b, nome="Lazer").one().id
        Lancamento.criar(b, "Do Bruno", "40", date(2026, 11, 7), c)
    for qs in ("", "?valor_min=1", "?data_de=2000-01-01", "?ordenar=valor&ordem=asc",
               "?q=barco", "?tipo=despesa"):
        h = html(logado_b.get("/lancamentos/" + qs))
        assert "Pizza" not in h and "Salário mensal" not in h and "Cinema" not in h


# ---------- filtro de categorias ----------
def test_categorias_filtro_por_tipo(logado):
    r = html(logado.get("/categorias/?tipo=receita"))
    assert "Salário" in r and "Renda extra" in r and "Alimentação" not in r
    r = html(logado.get("/categorias/?tipo=despesa"))
    assert "Alimentação" in r and "Salário" not in r
    r = html(logado.get("/categorias/"))
    assert "Salário" in r and "Alimentação" in r


def test_categorias_filtro_invalido_mostra_todas(logado):
    r = logado.get("/categorias/?tipo=xyz")
    assert r.status_code == 200 and "Alimentação" in html(r) and "Salário" in html(r)


def test_categorias_filtro_nao_mostra_de_outro_usuario(app, usuario, logado_b):
    with app.app_context():
        Categoria.criar(usuario, "SoDaAna", "receita")
    assert "SoDaAna" not in html(logado_b.get("/categorias/?tipo=receita"))


# ---------- seletor de mês no resumo ----------
def test_resumo_tem_seletor_de_mes_e_ano(logado):
    h = html(logado.get("/?mes=3&ano=2026"))
    assert 'name="mes"' in h and 'name="ano"' in h
    assert '<option value="3" selected>Março</option>' in h
    assert 'value="2026"' in h
    assert "Resumo de Março de 2026" in h


def test_resumo_escolhendo_outro_mes_mostra_so_aquele_mes(logado, dados):
    h = html(logado.get("/?mes=10&ano=2026"))
    assert "Resumo de Outubro de 2026" in h and "Cinema" in h
    assert "Pizza" not in h


@pytest.mark.parametrize("qs", ["mes=13&ano=2026", "mes=0", "mes=abc&ano=xyz", "ano=99999",
                                "mes=-1&ano=-5", "mes=&ano="])
def test_resumo_entrada_invalida_cai_no_mes_atual(logado, qs):
    r = logado.get("/?" + qs)
    assert r.status_code == 200
    hoje = date.today()
    assert str(hoje.year) in html(r) and "Resumo de" in html(r)


def test_resumo_nao_mostra_dados_de_outro_usuario(app, dados, logado_b):
    assert "Cinema" not in html(logado_b.get("/?mes=10&ano=2026"))


# ---------- header e layout ----------
def test_header_tem_conta_separada_do_menu(logado):
    h = html(logado.get("/"))
    assert 'class="conta"' in h and 'class="menu"' in h
    assert "Ana" in h and "Sair" in h


def test_resumo_nao_tem_botao_novo_lancamento(logado):
    assert "+ Novo lançamento" not in html(logado.get("/"))


def test_resumo_tem_abas_para_o_celular(logado):
    h = html(logado.get("/"))
    assert 'role="tablist"' in h and h.count('role="tab"') == 2
    assert 'id="painel-categorias"' in h and 'id="painel-ultimos"' in h
    assert 'aria-selected="true"' in h and "Por categoria" in h and "Últimos lançamentos" in h


def test_resumo_seletor_de_mes_aplica_sozinho_e_fica_na_mesma_barra(logado):
    h = html(logado.get("/"))
    assert 'class="mes-bar"' in h and "data-auto" in h
    assert h.index("Mês anterior") < h.index('name="mes"') < h.index("Próximo mês")


def test_filtros_de_lancamentos_aplicam_sozinhos_e_tem_rotulos(logado):
    h = html(logado.get("/lancamentos/"))
    assert "filtros-grid" in h and "data-auto" in h
    for rotulo in ("Buscar", "Tipo", "Categoria", "Data de", "Data até", "Valor mínimo",
                   "Valor máximo", "Ordenar por", "Ordem", "Mais filtros"):
        assert rotulo in h
    assert '<noscript><button' in h  # sem JavaScript ainda dá para filtrar


def test_categorias_filtro_aplica_sozinho(logado):
    h = html(logado.get("/categorias/"))
    assert "data-auto" in h and "Só receitas" in h


def test_botao_de_lote_comeca_pelo_javascript(logado):
    assert "data-lote-btn" in html(logado.get("/lancamentos/"))


def test_tabelas_usam_classe_responsiva(logado, dados):
    assert 'class="resp resp-sel"' in html(logado.get("/lancamentos/"))
    assert 'class="resp"' in html(logado.get("/categorias/"))
    assert 'class="resp"' in html(logado.get("/"))


def test_limpar_filtros_so_aparece_com_filtro_ativo(logado):
    assert "Limpar filtros" not in html(logado.get("/lancamentos/"))
    assert "Limpar filtros" in html(logado.get("/lancamentos/?tipo=receita"))
    assert "Limpar filtros" in html(logado.get("/lancamentos/?ordenar=valor"))


def test_mais_filtros_abre_sozinho_quando_ha_filtro_avancado(logado):
    assert "<details class=\"mais-filtros\" >" in html(logado.get("/lancamentos/"))
    assert "<details class=\"mais-filtros\" open>" in html(logado.get("/lancamentos/?valor_min=10"))
