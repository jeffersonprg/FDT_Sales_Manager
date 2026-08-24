from datetime import datetime

import pytest

from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.cliente_service import ClienteService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService


def test_criar_e_buscar_cliente(banco_temporario):
    cliente = Cliente(
        nome="Maria Silva",
        email="maria@email.pt",
        pais="Portugal",
        tipo_documento="NIF",
        numero_documento="123456789"
    )

    cliente_id = ClienteService.criar_cliente(cliente)

    assert cliente_id is not None

    cliente_encontrado = ClienteService.buscar_cliente(cliente_id)

    assert cliente_encontrado is not None
    assert cliente_encontrado.id == cliente_id
    assert cliente_encontrado.nome == "Maria Silva"
    assert cliente_encontrado.email == "maria@email.pt"


def test_listar_clientes(banco_temporario):
    ClienteService.criar_cliente(
        Cliente(nome="Ana Costa", email="ana@email.pt")
    )

    ClienteService.criar_cliente(
        Cliente(nome="Bruno Santos", email="bruno@email.pt")
    )

    clientes = ClienteService.listar_clientes()

    assert len(clientes) == 2
    assert clientes[0].nome == "Ana Costa"
    assert clientes[1].nome == "Bruno Santos"


def test_criacao_atribui_id_e_converte_datas(banco_temporario):
    cliente = Cliente(nome="Cliente com ID")

    cliente_id = ClienteService.criar_cliente(cliente)
    encontrado = ClienteService.buscar_cliente(cliente_id)

    assert cliente.id == cliente_id
    assert encontrado is not None
    assert isinstance(encontrado.criado_em, datetime)
    assert isinstance(encontrado.atualizado_em, datetime)


def test_email_e_documento_sao_unicos_sem_diferenciar_caixa(
    banco_temporario
):
    ClienteService.criar_cliente(
        Cliente(
            nome="Primeiro",
            email="pessoa@email.pt",
            numero_documento="ABC123"
        )
    )

    with pytest.raises(ValueError, match="este email"):
        ClienteService.criar_cliente(
            Cliente(nome="Segundo", email="PESSOA@EMAIL.PT")
        )

    with pytest.raises(ValueError, match="número de documento"):
        ClienteService.criar_cliente(
            Cliente(nome="Terceiro", numero_documento="abc123")
        )


def test_atualizacao_revalida_cliente(banco_temporario):
    cliente_id = ClienteService.criar_cliente(
        Cliente(nome="Cliente válido")
    )
    cliente = ClienteService.buscar_cliente(cliente_id)
    assert cliente is not None

    cliente.nome = "   "

    with pytest.raises(ValueError, match="nome do cliente"):
        ClienteService.atualizar_cliente(cliente)


def test_atualizar_cliente_inexistente_retorna_false(banco_temporario):
    atualizado = ClienteService.atualizar_cliente(
        Cliente(id=9999, nome="Inexistente")
    )

    assert atualizado is False


def test_remocao_logica_preserva_historico_e_permite_reativar(
    banco_temporario
):
    cliente_id = ClienteService.criar_cliente(
        Cliente(nome="Cliente com histórico")
    )
    produto_id = ProdutoService.criar_produto(
        Produto(nome="Produto histórico", preco=25)
    )
    pedido = Pedido(cliente_id=cliente_id)
    pedido.adicionar_item(
        ItemPedido(produto_id=produto_id, preco_unitario=25)
    )
    PedidoService.criar_pedido(pedido)

    assert ClienteService.remover_cliente(cliente_id) is True
    assert ClienteService.buscar_cliente(cliente_id) is None

    inativo = ClienteService.buscar_cliente(
        cliente_id,
        incluir_inativos=True
    )
    assert inativo is not None
    assert inativo.estado == "INATIVO"
    assert len(PedidoService.listar_pedidos(cliente_id)) == 1

    assert ClienteService.reativar_cliente(cliente_id) is True
    assert ClienteService.buscar_cliente(cliente_id) is not None


def test_atualizar_cliente(banco_temporario):
    cliente_id = ClienteService.criar_cliente(
        Cliente(
            nome="Carlos Mendes",
            telefone="910000000"
        )
    )

    cliente = ClienteService.buscar_cliente(cliente_id)

    assert cliente is not None

    cliente.telefone = "919999999"
    cliente.observacoes = "Cliente atualizado no teste."

    ClienteService.atualizar_cliente(cliente)

    cliente_atualizado = ClienteService.buscar_cliente(cliente_id)

    assert cliente_atualizado is not None
    assert cliente_atualizado.telefone == "919999999"
    assert cliente_atualizado.observacoes == "Cliente atualizado no teste."


def test_remover_cliente(banco_temporario):
    cliente_id = ClienteService.criar_cliente(
        Cliente(nome="Cliente Temporário")
    )

    removido = ClienteService.remover_cliente(cliente_id)

    assert removido is True
    assert ClienteService.buscar_cliente(cliente_id) is None


def test_remover_cliente_inexistente(banco_temporario):
    removido = ClienteService.remover_cliente(9999)

    assert removido is False
    
def test_pesquisar_clientes_por_nome(
    banco_temporario
):
    ClienteService.criar_cliente(
        Cliente(
            nome="Maria Silva",
            email="maria@email.pt"
        )
    )

    ClienteService.criar_cliente(
        Cliente(
            nome="João Costa",
            email="joao@email.pt"
        )
    )

    clientes = ClienteService.pesquisar_clientes(
        "maria"
    )

    assert len(clientes) == 1
    assert clientes[0].nome == "Maria Silva"


def test_pesquisar_clientes_por_diferentes_campos(
    banco_temporario
):
    ClienteService.criar_cliente(
        Cliente(
            nome="Ana Ferreira",
            empresa="FDT Academy",
            morada="Rua do Comércio, Porto",
            telefone="912345678",
            email="ana@fdt.pt",
            pais="Portugal",
            tipo_documento="NIF",
            numero_documento="123456789"
        )
    )

    pesquisas = [
        "FDT Academy",
        "912345678",
        "ana@fdt.pt",
        "123456789",
        "Porto",
        "Portugal"
    ]

    for termo in pesquisas:
        clientes = ClienteService.pesquisar_clientes(
            termo
        )

        assert len(clientes) == 1
        assert clientes[0].nome == "Ana Ferreira"


def test_pesquisar_clientes_sem_resultados(
    banco_temporario
):
    ClienteService.criar_cliente(
        Cliente(nome="Cliente Existente")
    )

    clientes = ClienteService.pesquisar_clientes(
        "Cliente Inexistente"
    )

    assert clientes == []


def test_pesquisa_vazia_lista_todos_os_clientes(
    banco_temporario
):
    ClienteService.criar_cliente(
        Cliente(nome="Bruno Santos")
    )

    ClienteService.criar_cliente(
        Cliente(nome="Ana Costa")
    )

    clientes = ClienteService.pesquisar_clientes(
        "   "
    )

    assert len(clientes) == 2
    assert clientes[0].nome == "Ana Costa"
    assert clientes[1].nome == "Bruno Santos"
