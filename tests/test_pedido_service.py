import pytest

from datetime import date, datetime
from src.database.database import get_connection
from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.cliente_service import ClienteService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def criar_cliente_teste() -> int:
    return ClienteService.criar_cliente(
        Cliente(
            nome="Cliente Pedido",
            email="pedido@email.pt"
        )
    )


def criar_produto_teste(
    nome: str,
    preco: float
) -> int:
    return ProdutoService.criar_produto(
        Produto(
            nome=nome,
            preco=preco,
            tipo_validade="VITALICIO"
        )
    )


def test_criar_e_buscar_pedido_com_itens(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_1_id = criar_produto_teste(
        "Curso Inicial",
        100
    )

    produto_2_id = criar_produto_teste(
        "Mentoria",
        49.90
    )

    pedido = Pedido(cliente_id=cliente_id)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_1_id,
            quantidade=2,
            preco_unitario=100
        )
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_2_id,
            quantidade=1,
            preco_unitario=49.90
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    pedido_encontrado = PedidoService.buscar_pedido(
        pedido_id
    )

    assert pedido_encontrado is not None
    assert pedido_encontrado.id == pedido_id
    assert pedido_encontrado.cliente_id == cliente_id
    assert pedido_encontrado.estado == "PENDENTE"
    assert pedido_encontrado.total == 249.90
    assert len(pedido_encontrado.itens) == 2

    assert pedido_encontrado.itens[0].pedido_id == pedido_id
    assert pedido_encontrado.itens[0].subtotal == 200
    assert pedido_encontrado.itens[1].subtotal == 49.90


def test_buscar_pedido_inexistente(
    banco_temporario
):
    pedido = PedidoService.buscar_pedido(9999)

    assert pedido is None


def test_pedido_exige_pelo_menos_um_item(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    pedido = Pedido(cliente_id=cliente_id)

    with pytest.raises(
        ValueError,
        match="O pedido deve possuir pelo menos um item"
    ):
        PedidoService.criar_pedido(pedido)


def test_pedido_nao_aceita_produto_desativado(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_id = criar_produto_teste(
        "Produto desativado",
        100
    )

    ProdutoService.desativar_produto(produto_id)

    pedido = Pedido(cliente_id=cliente_id)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    with pytest.raises(
        ValueError,
        match="está desativado"
    ):
        PedidoService.criar_pedido(pedido)

    connection = get_connection()

    quantidade_pedidos = connection.execute("""
        SELECT COUNT(*) AS total
        FROM pedidos
    """).fetchone()["total"]

    quantidade_itens = connection.execute("""
        SELECT COUNT(*) AS total
        FROM itens_pedido
    """).fetchone()["total"]

    connection.close()

    assert quantidade_pedidos == 0
    assert quantidade_itens == 0


def test_pedido_nao_aceita_cliente_inexistente(
    banco_temporario
):
    produto_id = criar_produto_teste(
        "Curso Teste",
        100
    )

    pedido = Pedido(cliente_id=9999)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    with pytest.raises(
        ValueError,
        match="Cliente não encontrado"
    ):
        PedidoService.criar_pedido(pedido)
        
def test_listar_pedidos(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_id = criar_produto_teste(
        "Produto para listagem",
        100
    )

    for quantidade in (1, 2):
        pedido = Pedido(cliente_id=cliente_id)

        pedido.adicionar_item(
            ItemPedido(
                produto_id=produto_id,
                quantidade=quantidade,
                preco_unitario=100
            )
        )

        PedidoService.criar_pedido(pedido)

    pedidos = PedidoService.listar_pedidos()

    assert len(pedidos) == 2
    assert all(
        pedido.cliente_id == cliente_id
        for pedido in pedidos
    )
    assert all(
        len(pedido.itens) == 1
        for pedido in pedidos
    )


def test_listar_pedidos_por_cliente(
    banco_temporario
):
    cliente_1_id = criar_cliente_teste()

    cliente_2_id = ClienteService.criar_cliente(
        Cliente(
            nome="Segundo Cliente",
            email="segundo@email.pt"
        )
    )

    produto_id = criar_produto_teste(
        "Produto por cliente",
        75
    )

    for cliente_id in (cliente_1_id, cliente_2_id):
        pedido = Pedido(cliente_id=cliente_id)

        pedido.adicionar_item(
            ItemPedido(
                produto_id=produto_id,
                quantidade=1,
                preco_unitario=75
            )
        )

        PedidoService.criar_pedido(pedido)

    pedidos_cliente_1 = PedidoService.listar_pedidos(
        cliente_id=cliente_1_id
    )

    assert len(pedidos_cliente_1) == 1
    assert pedidos_cliente_1[0].cliente_id == cliente_1_id


def test_atualizar_estado_pedido(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_id = criar_produto_teste(
        "Produto estado",
        100
    )

    pedido = Pedido(cliente_id=cliente_id)

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    atualizado = PedidoService.atualizar_estado_pedido(
        pedido_id,
        "pago"
    )

    pedido_atualizado = PedidoService.buscar_pedido(
        pedido_id
    )

    assert atualizado is True
    assert pedido_atualizado is not None
    assert pedido_atualizado.estado == "PAGO"


def test_atualizar_estado_invalido(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="O estado deve ser"
    ):
        PedidoService.atualizar_estado_pedido(
            1,
            "ENVIADO"
        )


def test_atualizar_estado_pedido_inexistente(
    banco_temporario
):
    atualizado = PedidoService.atualizar_estado_pedido(
        9999,
        "PAGO"
    )

    assert atualizado is False
def test_produto_temporario_calcula_periodo_de_acesso(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso de 30 dias",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=30
        )
    )

    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 2, 10, 0)
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=datetime(2026, 8, 2, 10, 0)
    )

    pedido_encontrado = PedidoService.buscar_pedido(
        pedido_id
    )

    assert pedido_encontrado is not None

    item = pedido_encontrado.itens[0]

    assert item.inicio_acesso == date(2026, 8, 2)
    assert item.fim_acesso == date(2026, 8, 31)


def test_produto_vitalicio_nao_possui_fim_de_acesso(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_id = criar_produto_teste(
        "Produto vitalício",
        200
    )

    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 2, 10, 0)
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=200
        )
    )

    pedido_id = PedidoService.criar_pedido(pedido)

    PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=datetime(2026, 8, 2, 10, 0)
    )

    pedido_encontrado = PedidoService.buscar_pedido(
        pedido_id
    )

    assert pedido_encontrado is not None

    item = pedido_encontrado.itens[0]

    assert item.inicio_acesso == date(2026, 8, 2)
    assert item.fim_acesso is None


def test_produto_temporario_rejeita_fim_incorreto(
    banco_temporario
):
    cliente_id = criar_cliente_teste()

    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso com validade",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=30
        )
    )

    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 2, 10, 0),
        estado="PAGO",
        pago_em=datetime(2026, 8, 2, 10, 0)
    )

    pedido.adicionar_item(
        ItemPedido(
            produto_id=produto_id,
            quantidade=1,
            preco_unitario=100,
            inicio_acesso=date(2026, 8, 2),
            fim_acesso=date(2026, 8, 20)
        )
    )

    with pytest.raises(
        ValueError,
        match="não corresponde à duração cadastrada"
    ):
        PedidoService.criar_pedido(pedido)

    connection = get_connection()

    quantidade_pedidos = connection.execute("""
        SELECT COUNT(*) AS total
        FROM pedidos
    """).fetchone()["total"]

    connection.close()

    assert quantidade_pedidos == 0


def test_acesso_comeca_na_data_de_pagamento(banco_temporario):
    cliente_id = criar_cliente_teste()
    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso pago depois",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=30
        )
    )
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 1, 10, 0)
    )
    pedido.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=100)
    )
    pedido_id = PedidoService.criar_pedido(pedido)

    antes = PedidoService.buscar_pedido(pedido_id)
    assert antes.itens[0].inicio_acesso is None

    PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=datetime(2026, 8, 10, 15, 0)
    )

    pago = PedidoService.buscar_pedido(pedido_id)
    assert pago is not None
    assert pago.pago_em == datetime(2026, 8, 10, 15, 0)
    assert pago.itens[0].inicio_acesso == date(2026, 8, 10)
    assert pago.itens[0].fim_acesso == date(2026, 9, 8)


def test_transicoes_de_estado_sao_controladas(banco_temporario):
    cliente_id = criar_cliente_teste()
    produto_id = criar_produto_teste("Produto transição", 100)
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 1, 10, 0)
    )
    pedido.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=100)
    )
    pedido_id = PedidoService.criar_pedido(pedido)

    PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=datetime(2026, 8, 2, 10, 0)
    )
    PedidoService.atualizar_estado_pedido(
        pedido_id,
        "CANCELADO",
        data_evento=datetime(2026, 8, 3, 10, 0)
    )

    cancelado = PedidoService.buscar_pedido(pedido_id)
    assert cancelado is not None
    assert cancelado.cancelado_em == datetime(2026, 8, 3, 10, 0)

    with pytest.raises(ValueError, match="Não é permitido"):
        PedidoService.atualizar_estado_pedido(
            pedido_id,
            "PAGO",
            data_evento=datetime(2026, 8, 4, 10, 0)
        )


def test_pedido_pendente_pode_ser_pago_apos_produto_desativado(
    banco_temporario
):
    cliente_id = criar_cliente_teste()
    produto_id = criar_produto_teste("Produto contratado", 100)
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 1, 10, 0)
    )
    pedido.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=90)
    )
    pedido_id = PedidoService.criar_pedido(pedido)
    ProdutoService.desativar_produto(produto_id)

    atualizado = PedidoService.atualizar_estado_pedido(
        pedido_id,
        "PAGO",
        data_evento=datetime(2026, 8, 2, 10, 0)
    )

    assert atualizado is True
    assert PedidoService.buscar_pedido(pedido_id).estado == "PAGO"


def test_cliente_inativo_nao_recebe_novo_pedido(banco_temporario):
    cliente_id = criar_cliente_teste()
    produto_id = criar_produto_teste("Produto cliente inativo", 100)
    ClienteService.remover_cliente(cliente_id)
    pedido = Pedido(cliente_id=cliente_id)
    pedido.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=100)
    )

    with pytest.raises(ValueError, match="cliente inativo"):
        PedidoService.criar_pedido(pedido)


def test_data_pagamento_nao_pode_anteceder_pedido(banco_temporario):
    cliente_id = criar_cliente_teste()
    produto_id = criar_produto_teste("Produto data", 100)
    pedido = Pedido(
        cliente_id=cliente_id,
        data_pedido=datetime(2026, 8, 10, 10, 0)
    )
    pedido.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=100)
    )
    pedido_id = PedidoService.criar_pedido(pedido)

    with pytest.raises(ValueError, match="anterior à data do pedido"):
        PedidoService.atualizar_estado_pedido(
            pedido_id,
            "PAGO",
            data_evento=datetime(2026, 8, 9, 10, 0)
        )
