from datetime import datetime

import pytest

from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.cliente_service import ClienteService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def preparar_dados():
    cliente_id = ClienteService.criar_cliente(
        Cliente(nome="Cliente Referência Externa")
    )

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Produto Referência Externa",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    return cliente_id, produto_id


def test_criar_pedido_com_referencia_externa(
    banco_temporario
):
    cliente_id, produto_id = preparar_dados()

    pedido = Pedido(
        cliente_id=cliente_id,
        referencia_externa="PED-IMPORT-001",
        data_pedido=datetime(2026, 8, 20, 10, 0)
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    pedido_guardado = PedidoService.buscar_pedido(
        pedido_id
    )

    assert pedido_guardado is not None
    assert (
        pedido_guardado.referencia_externa
        == "PED-IMPORT-001"
    )


def test_buscar_pedido_por_referencia_externa(
    banco_temporario
):
    cliente_id, produto_id = preparar_dados()

    pedido = Pedido(
        cliente_id=cliente_id,
        referencia_externa="PED-IMPORT-002"
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    PedidoService.criar_pedido(pedido)

    encontrado = (
        PedidoService.buscar_por_referencia_externa(
            "PED-IMPORT-002"
        )
    )

    assert encontrado is not None
    assert (
        encontrado.referencia_externa
        == "PED-IMPORT-002"
    )
    assert len(encontrado.itens) == 1


def test_referencia_externa_vazia_vira_none(
    banco_temporario
):
    pedido = Pedido(
        cliente_id=1,
        referencia_externa="   "
    )

    assert pedido.referencia_externa is None


def test_busca_rejeita_referencia_vazia(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="referência externa não pode estar vazia"
    ):
        PedidoService.buscar_por_referencia_externa(
            "   "
        )


def test_referencia_externa_e_unica_sem_diferenciar_caixa(
    banco_temporario
):
    cliente_id, produto_id = preparar_dados()

    primeiro = Pedido(
        cliente_id=cliente_id,
        referencia_externa="PED-CASE-001"
    )
    primeiro.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=100)
    )
    PedidoService.criar_pedido(primeiro)

    segundo = Pedido(
        cliente_id=cliente_id,
        referencia_externa="ped-case-001"
    )
    segundo.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=100)
    )

    with pytest.raises(ValueError, match="referência externa"):
        PedidoService.criar_pedido(segundo)

    encontrado = PedidoService.buscar_por_referencia_externa(
        "ped-case-001"
    )
    assert encontrado is not None
    assert encontrado.id == primeiro.id
