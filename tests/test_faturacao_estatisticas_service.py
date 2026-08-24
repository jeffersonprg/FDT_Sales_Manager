from datetime import date, datetime

import pytest

from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.cliente_service import ClienteService
from src.services.dashboard_service import DashboardService
from src.services.estatisticas_service import EstatisticasService
from src.services.faturacao_service import FaturacaoService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def preparar_vendas() -> tuple[int, int]:
    cliente_id = ClienteService.criar_cliente(
        Cliente(nome="Cliente das estatísticas")
    )
    produto_a_id = ProdutoService.criar_produto(
        Produto(nome="Produto A estatísticas", preco=100)
    )
    produto_b_id = ProdutoService.criar_produto(
        Produto(nome="Produto B estatísticas", preco=50)
    )

    pedido_1 = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 1, 9, 0)
    )
    pedido_1.adicionar_item(
        ItemPedido(
            produto_id=produto_a_id,
            quantidade=2,
            preco_unitario=90
        )
    )
    pedido_1.adicionar_item(
        ItemPedido(
            produto_id=produto_b_id,
            quantidade=1,
            preco_unitario=50
        )
    )
    pedido_1_id = PedidoService.criar_pedido(pedido_1)
    PedidoService.atualizar_estado_pedido(
        pedido_1_id,
        "PAGO",
        data_evento=datetime(2026, 8, 2, 10, 0)
    )

    pedido_2 = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 10, 9, 0)
    )
    pedido_2.adicionar_item(
        ItemPedido(
            produto_id=produto_b_id,
            quantidade=2,
            preco_unitario=50
        )
    )
    pedido_2_id = PedidoService.criar_pedido(pedido_2)
    PedidoService.atualizar_estado_pedido(
        pedido_2_id,
        "PAGO",
        data_evento=datetime(2026, 8, 11, 10, 0)
    )

    return produto_a_id, produto_b_id


def test_faturacao_resume_apenas_pedidos_pagos(banco_temporario):
    preparar_vendas()

    resumo = FaturacaoService.obter_resumo()

    assert resumo["total_pedidos_pagos"] == 2
    assert resumo["faturacao_total"] == 330.0
    assert resumo["ticket_medio"] == 165.0


def test_faturacao_filtra_por_data_de_pagamento(banco_temporario):
    preparar_vendas()

    resumo = FaturacaoService.obter_resumo(
        data_inicio=date(2026, 8, 10),
        data_fim=date(2026, 8, 20)
    )
    pedidos = FaturacaoService.listar_pedidos_faturados(
        data_inicio=date(2026, 8, 10),
        data_fim=date(2026, 8, 20)
    )

    assert resumo["total_pedidos_pagos"] == 1
    assert resumo["faturacao_total"] == 100.0
    assert len(pedidos) == 1
    assert pedidos[0].pago_em == datetime(2026, 8, 11, 10, 0)


def test_faturacao_rejeita_periodo_invertido(banco_temporario):
    with pytest.raises(ValueError, match="data inicial"):
        FaturacaoService.obter_resumo(
            data_inicio=date(2026, 8, 20),
            data_fim=date(2026, 8, 1)
        )


def test_estatisticas_agregam_vendas_por_produto(banco_temporario):
    produto_a_id, produto_b_id = preparar_vendas()

    resumo = EstatisticasService.obter_resumo_vendas()
    produtos = EstatisticasService.vendas_por_produto()

    assert resumo == {
        "total_pedidos": 2,
        "quantidade_vendida": 5,
        "faturacao_total": 330.0,
        "media_por_pedido": 165.0
    }
    assert [item["produto_id"] for item in produtos] == [
        produto_b_id,
        produto_a_id
    ]
    assert produtos[0]["quantidade_vendida"] == 3
    assert produtos[0]["faturacao_total"] == 150.0
    assert produtos[1]["quantidade_vendida"] == 2
    assert produtos[1]["faturacao_total"] == 180.0


def test_dashboard_inclui_produto_mais_vendido_e_ultimos_pedidos(
    banco_temporario
):
    _, produto_b_id = preparar_vendas()

    resumo = DashboardService.obter_resumo(limite_ultimos_pedidos=1)

    assert resumo["produto_mais_vendido"]["produto_id"] == produto_b_id
    assert resumo["produto_mais_vendido"]["quantidade_vendida"] == 3
    assert len(resumo["ultimos_pedidos"]) == 1
