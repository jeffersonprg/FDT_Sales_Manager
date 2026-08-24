import pytest

from src.models.cliente import Cliente


def test_criar_cliente_com_valores_padrao():
    cliente = Cliente(
        nome="Jefferson Gomes",
        email="jefferson@email.pt"
    )

    assert cliente.id is None
    assert cliente.nome == "Jefferson Gomes"
    assert cliente.email == "jefferson@email.pt"
    assert cliente.pais == "Portugal"
    assert cliente.empresa is None
    assert cliente.criado_em is None


def test_cliente_normaliza_dados():
    cliente = Cliente(
        nome="  Maria Silva  ",
        email="  MARIA@EMAIL.PT  ",
        tipo_documento="nif",
        numero_documento=" 123456789 ",
        estado="ativo"
    )

    assert cliente.nome == "Maria Silva"
    assert cliente.email == "maria@email.pt"
    assert cliente.tipo_documento == "NIF"
    assert cliente.numero_documento == "123456789"
    assert cliente.estado == "ATIVO"


def test_cliente_rejeita_nome_vazio():
    with pytest.raises(
        ValueError,
        match="O nome do cliente é obrigatório"
    ):
        Cliente(nome="   ")


def test_cliente_rejeita_email_invalido():
    with pytest.raises(
        ValueError,
        match="O email do cliente não é válido"
    ):
        Cliente(nome="Cliente", email="email-invalido")


def test_cliente_rejeita_estado_invalido():
    with pytest.raises(
        ValueError,
        match="ATIVO ou INATIVO"
    ):
        Cliente(nome="Cliente", estado="BLOQUEADO")
