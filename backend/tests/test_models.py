from datetime import date
from decimal import Decimal

import pytest

from app.models import Categoria, Lancamento
from app.models.categoria import ValidacaoError


@pytest.fixture(autouse=True)
def _uid(usuario):
    """Todos os testes deste arquivo rodam com o usuário A criado."""


def cat(nome, uid=1):
    return Categoria.query.filter_by(usuario_id=uid, nome=nome).one()


# ---------- Categoria ----------
def test_cria_categoria(ctx):
    c = Categoria.criar(1, "Investimentos", "receita")
    assert c.id and c.tipo == "receita"


def test_categoria_nome_obrigatorio(ctx):
    with pytest.raises(ValidacaoError):
        Categoria.criar(1, "   ", "despesa")


def test_categoria_tipo_invalido(ctx):
    with pytest.raises(ValidacaoError):
        Categoria.criar(1, "X", "outro")


def test_categoria_duplicada_ignora_maiusculas(ctx):
    with pytest.raises(ValidacaoError):
        Categoria.criar(1, "lazer", "despesa")  # "Lazer" já existe


def test_nao_exclui_categoria_com_lancamentos(ctx):
    c = cat("Lazer")
    Lancamento.criar(1, "Cinema", "30", date(2026, 11, 1), c.id)
    with pytest.raises(ValidacaoError):
        c.excluir()


def test_exclui_categoria_sem_lancamentos(ctx):
    c = Categoria.criar(1, "Temp", "despesa")
    c.excluir()
    assert Categoria.query.filter_by(nome="Temp").first() is None


# ---------- Lancamento ----------
def test_cria_lancamento_aceita_virgula_decimal(ctx):
    l = Lancamento.criar(1, "Mercado", "150,50", "2026-11-03", cat("Alimentação").id)
    assert l.valor == Decimal("150.50")
    assert l.tipo == "despesa"


@pytest.mark.parametrize("valor", ["0", "-10", "abc", "", None, "nan", "inf"])
def test_valor_invalido(ctx, valor):
    with pytest.raises(ValidacaoError):
        Lancamento.criar(1, "X", valor, "2026-11-03", cat("Lazer").id)


def test_descricao_obrigatoria(ctx):
    with pytest.raises(ValidacaoError):
        Lancamento.criar(1, "  ", "10", "2026-11-03", cat("Lazer").id)


def test_data_invalida(ctx):
    with pytest.raises(ValidacaoError):
        Lancamento.criar(1, "X", "10", "31/02/2026", cat("Lazer").id)


def test_categoria_inexistente(ctx):
    with pytest.raises(ValidacaoError):
        Lancamento.criar(1, "X", "10", "2026-11-03", 9999)


def test_atualiza_lancamento(ctx):
    l = Lancamento.criar(1, "Cinema", "30", "2026-11-03", cat("Lazer").id)
    l.atualizar("Teatro", "45,90", "2026-11-04", cat("Lazer").id, "com amigos")
    assert l.descricao == "Teatro" and l.valor == Decimal("45.90")


def test_resumo_mensal(ctx):
    Lancamento.criar(1, "Salário", "3000", "2026-11-05", cat("Salário").id)
    Lancamento.criar(1, "Mercado", "400,25", "2026-11-06", cat("Alimentação").id)
    Lancamento.criar(1, "Cinema", "50", "2026-11-07", cat("Lazer").id)
    Lancamento.criar(1, "Outro mês", "999", "2026-10-07", cat("Lazer").id)

    lancs = Lancamento.do_mes(1, 2026, 11)
    r = Lancamento.resumo(lancs)
    assert len(lancs) == 3
    assert r["receitas"] == Decimal("3000.00")
    assert r["despesas"] == Decimal("450.25")
    assert r["saldo"] == Decimal("2549.75")
    assert r["por_categoria"][0]["nome"] == "Salário"


def test_resumo_vazio(ctx):
    r = Lancamento.resumo([])
    assert r["saldo"] == Decimal("0.00") and r["por_categoria"] == []
