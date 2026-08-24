from datetime import date, datetime

from src.models.item_pedido import ItemPedido
from src.models.lead import Lead
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.acesso_service import AcessoService
from src.services.cliente_service import ClienteService
from src.services.dashboard_service import DashboardService
from src.services.lead_service import LeadService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def test_fluxo_completo_do_minicrm(banco_temporario):
    # 1. Criar um produto
    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Completo de Trading",
            categoria="Curso",
            preco=300,
            tipo_validade="TEMPORARIO",
            duracao_dias=30
        )
    )

    # 2. Criar um lead interessado no produto
    lead_id = LeadService.criar_lead(
        Lead(
            nome="Cliente do Fluxo Completo",
            email="fluxo.completo@email.pt",
            origem="Instagram",
            estado="QUALIFICADO",
            produto_interesse_id=produto_id
        )
    )

    # 3. Converter o lead em cliente
    cliente_id = LeadService.converter_em_cliente(
        lead_id=lead_id,
        pais="Portugal"
    )

    cliente = ClienteService.buscar_cliente(cliente_id)
    lead = LeadService.buscar_lead(lead_id)

    assert cliente is not None
    assert cliente.nome == "Cliente do Fluxo Completo"

    assert lead is not None
    assert lead.estado == "CONVERTIDO"
    assert lead.cliente_id == cliente_id

    # 4. Criar um pedido
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 2, 10, 0)
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=300
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    # 5. Confirmar o pagamento
    atualizado = PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=datetime(2026, 8, 2, 10, 0)
    )

    assert atualizado is True

    pedido_guardado = PedidoService.buscar_pedido(pedido_id)

    assert pedido_guardado is not None
    assert pedido_guardado.estado == "PAGO"
    assert pedido_guardado.total == 300
    assert len(pedido_guardado.itens) == 1

    # 6. Confirmar o acesso ao produto
    acessos = AcessoService.listar_acessos_cliente(
        cliente_id=cliente_id,
        apenas_ativos=True,
        data_referencia=date(2026, 8, 15)
    )

    assert len(acessos) == 1
    assert acessos[0]["produto_id"] == produto_id
    assert acessos[0]["produto_nome"] == (
        "Curso Completo de Trading"
    )
    assert acessos[0]["inicio_acesso"] == date(2026, 8, 2)
    assert acessos[0]["fim_acesso"] == date(2026, 8, 31)
    assert acessos[0]["ativo"] is True

    # 7. Confirmar os indicadores do dashboard
    resumo = DashboardService.obter_resumo()

    assert resumo["total_clientes"] == 1
    assert resumo["total_produtos_ativos"] == 1
    assert resumo["total_leads"] == 1
    assert resumo["leads_convertidos"] == 1
    assert resumo["taxa_conversao"] == 100.0
    assert resumo["total_pedidos"] == 1
    assert resumo["pedidos_pagos"] == 1
    assert resumo["faturacao_total"] == 300.0
    assert resumo["ticket_medio"] == 300.0
