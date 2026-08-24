from datetime import date, datetime

import pytest

from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.acesso_service import AcessoService
from src.services.cliente_service import ClienteService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def criar_cliente_acesso() -> int:
    return ClienteService.criar_cliente(
        Cliente(
            nome="Cliente Acesso",
            email="cliente.acesso@email.pt"
        )
    )


def criar_pedido_pago(
    cliente_id: int,
    produto_id: int,
    preco: float,
    data_pedido: datetime
) -> int:
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=data_pedido
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=preco
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=data_pedido
    )

    return pedido_id


def test_listar_acesso_vitalicio_ativo(
    banco_temporario
):
    cliente_id = criar_cliente_acesso()

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Mentoria Vitalícia",
            preco=500,
            tipo_validade="VITALICIO"
        )
    )

    criar_pedido_pago(
        cliente_id=cliente_id,
        produto_id=produto_id,
        preco=500,
        data_pedido=datetime(2026, 8, 1, 10, 0)
    )

    acessos = AcessoService.listar_acessos_cliente(
        cliente_id=cliente_id,
        data_referencia=date(2027, 8, 1)
    )

    assert len(acessos) == 1
    assert acessos[0]["produto_nome"] == (
        "Mentoria Vitalícia"
    )
    assert acessos[0]["tipo_validade"] == "VITALICIO"
    assert acessos[0]["fim_acesso"] is None
    assert acessos[0]["ativo"] is True


def test_listar_acesso_temporario_ativo(
    banco_temporario
):
    cliente_id = criar_cliente_acesso()

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso de 30 dias",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=30
        )
    )

    criar_pedido_pago(
        cliente_id=cliente_id,
        produto_id=produto_id,
        preco=100,
        data_pedido=datetime(2026, 8, 1, 10, 0)
    )

    acessos = AcessoService.listar_acessos_cliente(
        cliente_id=cliente_id,
        apenas_ativos=True,
        data_referencia=date(2026, 8, 15)
    )

    assert len(acessos) == 1
    assert acessos[0]["inicio_acesso"] == date(
        2026, 8, 1
    )
    assert acessos[0]["fim_acesso"] == date(
        2026, 8, 30
    )
    assert acessos[0]["ativo"] is True


def test_acesso_expirado_nao_aparece_com_filtro_ativo(
    banco_temporario
):
    cliente_id = criar_cliente_acesso()

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Expirado",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=30
        )
    )

    criar_pedido_pago(
        cliente_id=cliente_id,
        produto_id=produto_id,
        preco=100,
        data_pedido=datetime(2026, 8, 1, 10, 0)
    )

    todos = AcessoService.listar_acessos_cliente(
        cliente_id=cliente_id,
        data_referencia=date(2026, 9, 1)
    )

    ativos = AcessoService.listar_acessos_cliente(
        cliente_id=cliente_id,
        apenas_ativos=True,
        data_referencia=date(2026, 9, 1)
    )

    assert len(todos) == 1
    assert todos[0]["ativo"] is False
    assert ativos == []


def test_pedido_pendente_nao_concede_acesso(
    banco_temporario
):
    cliente_id = criar_cliente_acesso()

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Pendente",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    pedido = Pedido(cliente_id=cliente_id)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    PedidoService.criar_pedido(pedido)

    acessos = AcessoService.listar_acessos_cliente(
        cliente_id
    )

    assert acessos == []


def test_acessos_rejeitam_cliente_inexistente(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="Cliente não encontrado"
    ):
        AcessoService.listar_acessos_cliente(9999)
