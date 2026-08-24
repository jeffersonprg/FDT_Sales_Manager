from datetime import date

import pytest

from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido


def test_item_pedido_calcula_subtotal():
    item = ItemPedido(
        produto_id=1,
        quantidade=3,
        preco_unitario=49.90
    )

    assert item.subtotal == 149.70


def test_item_pedido_nao_aceita_quantidade_invalida():
    with pytest.raises(
        ValueError,
        match="A quantidade deve ser superior a zero"
    ):
        ItemPedido(
            produto_id=1,
            quantidade=0,
            preco_unitario=100
        )


def test_item_pedido_nao_aceita_preco_negativo():
    with pytest.raises(
        ValueError,
        match="O preço unitário não pode ser negativo"
    ):
        ItemPedido(
            produto_id=1,
            quantidade=1,
            preco_unitario=-10
        )


def test_item_pedido_valida_subtotal():
    with pytest.raises(
        ValueError,
        match="O subtotal deve corresponder"
    ):
        ItemPedido(
            produto_id=1,
            quantidade=2,
            preco_unitario=100,
            subtotal=150
        )


def test_item_pedido_valida_periodo_de_acesso():
    with pytest.raises(
        ValueError,
        match="A data de fim não pode ser anterior"
    ):
        ItemPedido(
            produto_id=1,
            quantidade=1,
            preco_unitario=100,
            inicio_acesso=date(2026, 8, 10),
            fim_acesso=date(2026, 8, 1)
        )


def test_criar_pedido():
    pedido = Pedido(
        cliente_id=1,
        estado="pendente"
    )

    assert pedido.cliente_id == 1
    assert pedido.estado == "PENDENTE"
    assert pedido.total == 0
    assert pedido.itens == []


def test_pedido_nao_aceita_estado_invalido():
    with pytest.raises(
        ValueError,
        match="O estado deve ser"
    ):
        Pedido(
            cliente_id=1,
            estado="ENVIADO"
        )


def test_adicionar_itens_calcula_total():
    pedido = Pedido(cliente_id=1)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=1,
            quantidade=2,
            preco_unitario=100
        )
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=2,
            quantidade=1,
            preco_unitario=49.90
        )
    )

    assert len(pedido.itens) == 2
    assert pedido.total == 249.90


def test_pedido_nao_aceita_produto_duplicado():
    pedido = Pedido(cliente_id=1)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=1,
            quantidade=1,
            preco_unitario=100
        )
    )

    with pytest.raises(
        ValueError,
        match="O produto já foi adicionado"
    ):
        pedido.adicionar_item(
            ItemPedido(
                produto_id=1,
                quantidade=2,
                preco_unitario=100
            )
        )