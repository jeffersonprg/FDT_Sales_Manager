from datetime import date, datetime

import pytest

from src.presentation import (
    NAVIGATION_ITEMS,
    formatar_data,
    formatar_moeda,
    formatar_opcao_entidade,
    formatar_texto,
    interpretar_data_filtro,
    interpretar_datetime_evento,
    interpretar_decimal,
    interpretar_id_opcao,
    interpretar_inteiro_opcional,
    montar_dashboard,
    texto_opcional,
)


def test_formatadores_da_interface():
    assert formatar_moeda(2696) == "€ 2.696,00"
    assert formatar_data(datetime(2026, 8, 25, 14, 30)) == "25/08/2026"
    assert formatar_data(datetime(2026, 8, 25, 14, 30), True) == "25/08/2026 14:30"
    assert formatar_texto(None) == "—"


def test_interpretar_data_filtro():
    assert interpretar_data_filtro(" 2026-08-25 ") == date(2026, 8, 25)
    assert interpretar_data_filtro("  ") is None
    with pytest.raises(ValueError, match="AAAA-MM-DD"):
        interpretar_data_filtro("25/08/2026")


def test_conversores_de_formulario():
    assert interpretar_decimal("€ 1.299,90", "preço") == 1299.9
    assert interpretar_decimal("499.50", "preço") == 499.5
    assert interpretar_inteiro_opcional(" 30 ", "duração") == 30
    assert interpretar_inteiro_opcional("", "duração") is None
    assert texto_opcional("  exemplo ") == "exemplo"
    assert texto_opcional("   ") is None


def test_conversores_de_formulario_rejeitam_valores_invalidos():
    with pytest.raises(ValueError, match="preço deve ser numérico"):
        interpretar_decimal("abc", "preço")
    with pytest.raises(ValueError, match="duração deve ser um número inteiro"):
        interpretar_inteiro_opcional("3.5", "duração")


def test_opcoes_de_entidades_do_formulario():
    opcao = formatar_opcao_entidade(12, "Formação Premium")
    assert opcao == "12 · Formação Premium"
    assert interpretar_id_opcao(opcao) == 12
    assert interpretar_id_opcao("— Sem produto —") is None
    with pytest.raises(ValueError, match="opção selecionada"):
        interpretar_id_opcao("produto sem identificador")


def test_interpretar_data_e_hora_de_evento():
    assert interpretar_datetime_evento("2026-08-26 14:30") == datetime(2026, 8, 26, 14, 30)
    assert interpretar_datetime_evento("  ") is None
    with pytest.raises(ValueError, match="AAAA-MM-DD HH:MM"):
        interpretar_datetime_evento("26/08/2026 14:30")


def test_navegacao_contem_todos_os_modulos():
    assert [item[0] for item in NAVIGATION_ITEMS] == [
        "dashboard", "clientes", "produtos", "leads", "pedidos", "csv", "relatorios",
        "configuracoes",
    ]


def test_montar_dashboard_vazio():
    dados = montar_dashboard({})
    assert len(dados["cards"]) == 6
    assert dados["taxa_conversao"] == "0.0%"
    assert dados["produto_destaque"] == "Nenhuma venda registada"
    assert dados["pedidos"] == []


def test_montar_dashboard_com_dados():
    dados = montar_dashboard({
        "total_clientes": 4,
        "total_produtos_ativos": 2,
        "leads_abertos": 3,
        "pedidos_pagos": 5,
        "faturacao_total": 2696,
        "ticket_medio": 539.2,
        "taxa_conversao": 25,
        "produto_mais_vendido": {
            "produto_nome": "Formação Premium", "quantidade_vendida": 4,
        },
        "ultimos_pedidos": [{
            "id": 9, "cliente_nome": "Ana Silva", "data_pedido": "2026-08-25T10:00:00",
            "estado": "PAGO", "total": 499,
        }],
    })
    assert dados["cards"][4][1] == "€ 2.696,00"
    assert dados["taxa_conversao"] == "25.0%"
    assert dados["produto_destaque"] == "Formação Premium · 4 vendidos"
    assert dados["pedidos"][0] == ("#9", "Ana Silva", "25/08/2026", "PAGO", "€ 499,00")
