from datetime import datetime

import pytest

from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.cliente_resumo_service import (
    ClienteResumoService
)
from src.services.cliente_service import ClienteService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def criar_cliente_resumo() -> int:
    return ClienteService.criar_cliente(
        Cliente(
            nome="Cliente Resumo",
            email="cliente.resumo@email.pt"
        )
    )


def criar_produto_resumo() -> int:
    return ProdutoService.criar_produto(
        Produto(
            nome="Produto Resumo",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )


def criar_pedido_resumo(
    cliente_id: int,
    produto_id: int,
    quantidade: int,
    estado: str,
    data_pedido: datetime
) -> int:
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=data_pedido
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=quantidade,
            preco_unitario=100
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    if estado != "PENDENTE":
        PedidoService.atualizar_estado_pedido(
            pedido_id,
            estado,
            data_evento=data_pedido
        )

    return pedido_id


def test_resumo_cliente_sem_pedidos(
    banco_temporario
):
    cliente_id = criar_cliente_resumo()

    resumo = ClienteResumoService.obter_resumo(
        cliente_id
    )

    assert resumo is not None
    assert resumo["cliente_id"] == cliente_id
    assert resumo["cliente_nome"] == "Cliente Resumo"
    assert resumo["total_pedidos"] == 0
    assert resumo["pedidos_pagos"] == 0
    assert resumo["pedidos_pendentes"] == 0
    assert resumo["pedidos_cancelados"] == 0
    assert resumo["faturacao_total"] == 0.0
    assert resumo["ticket_medio"] == 0.0
    assert resumo["ultima_compra"] is None


def test_resumo_cliente_com_pedidos(
    banco_temporario
):
    cliente_id = criar_cliente_resumo()
    produto_id = criar_produto_resumo()

    data_compra = datetime(
        2026,
        8,
        2,
        15,
        30
    )

    criar_pedido_resumo(
        cliente_id=cliente_id,
        produto_id=produto_id,
        quantidade=2,
        estado="PAGO",
        data_pedido=data_compra
    )

    criar_pedido_resumo(
        cliente_id=cliente_id,
        produto_id=produto_id,
        quantidade=1,
        estado="PENDENTE",
        data_pedido=datetime(2026, 8, 3, 10, 0)
    )

    criar_pedido_resumo(
        cliente_id=cliente_id,
        produto_id=produto_id,
        quantidade=1,
        estado="CANCELADO",
        data_pedido=datetime(2026, 8, 4, 10, 0)
    )

    resumo = ClienteResumoService.obter_resumo(
        cliente_id
    )

    assert resumo is not None
    assert resumo["total_pedidos"] == 3
    assert resumo["pedidos_pagos"] == 1
    assert resumo["pedidos_pendentes"] == 1
    assert resumo["pedidos_cancelados"] == 1
    assert resumo["faturacao_total"] == 200.0
    assert resumo["ticket_medio"] == 200.0
    assert resumo["ultima_compra"] == data_compra


def test_resumo_cliente_inexistente(
    banco_temporario
):
    resumo = ClienteResumoService.obter_resumo(9999)

    assert resumo is None


def test_resumo_rejeita_id_invalido(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="O ID do cliente deve ser válido"
    ):
        ClienteResumoService.obter_resumo(0)
