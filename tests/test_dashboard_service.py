from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.lead import Lead
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.cliente_service import ClienteService
from src.services.dashboard_service import DashboardService
from src.services.lead_service import LeadService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def test_resumo_dashboard_vazio(banco_temporario):
    resumo = DashboardService.obter_resumo()

    assert resumo["total_clientes"] == 0
    assert resumo["total_produtos_ativos"] == 0
    assert resumo["total_leads"] == 0
    assert resumo["leads_abertos"] == 0
    assert resumo["leads_convertidos"] == 0
    assert resumo["total_pedidos"] == 0
    assert resumo["pedidos_pagos"] == 0
    assert resumo["faturacao_total"] == 0.0
    assert resumo["ticket_medio"] == 0.0
    assert resumo["taxa_conversao"] == 0.0


def test_resumo_dashboard_com_dados(banco_temporario):
    cliente_id = ClienteService.criar_cliente(
        Cliente(
            nome="Cliente Dashboard",
            email="cliente.dashboard@email.pt"
        )
    )

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Dashboard",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    pedido_pago = Pedido(cliente_id=cliente_id)

    pedido_pago.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=2,
            preco_unitario=100
        )
    )

    pedido_pago_id = PedidoService.criar_pedido(
        pedido_pago
    )

    PedidoService.atualizar_estado_pedido(
        pedido_pago_id,
        "PAGO"
    )

    pedido_cancelado = Pedido(cliente_id=cliente_id)

    pedido_cancelado.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    pedido_cancelado_id = PedidoService.criar_pedido(
        pedido_cancelado
    )

    PedidoService.atualizar_estado_pedido(
        pedido_cancelado_id,
        "CANCELADO"
    )

    LeadService.criar_lead(
        Lead(
            nome="Lead em aberto",
            estado="QUALIFICADO"
        )
    )

    lead_convertido_id = LeadService.criar_lead(
        Lead(
            nome="Lead convertido",
            email="lead.convertido@email.pt",
            estado="QUALIFICADO"
        )
    )

    LeadService.converter_em_cliente(
        lead_convertido_id
    )

    resumo = DashboardService.obter_resumo()

    assert resumo["total_clientes"] == 2
    assert resumo["total_produtos_ativos"] == 1

    assert resumo["total_leads"] == 2
    assert resumo["leads_abertos"] == 1
    assert resumo["leads_convertidos"] == 1
    assert resumo["taxa_conversao"] == 50.0

    assert resumo["total_pedidos"] == 2
    assert resumo["pedidos_pagos"] == 1

    assert resumo["faturacao_total"] == 200.0
    assert resumo["ticket_medio"] == 200.0


def test_dashboard_nao_conta_produto_desativado(
    banco_temporario
):
    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Produto desativado do dashboard",
            preco=50,
            tipo_validade="VITALICIO"
        )
    )

    ProdutoService.desativar_produto(produto_id)

    resumo = DashboardService.obter_resumo()

    assert resumo["total_produtos_ativos"] == 0