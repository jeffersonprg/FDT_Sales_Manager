import pytest

from src.models.produto import Produto


def test_criar_produto_vitalicio():
    produto = Produto(
        nome="Mentoria Premium",
        categoria="Mentoria",
        preco=499.90,
        tipo_validade="VITALICIO"
    )

    assert produto.nome == "Mentoria Premium"
    assert produto.preco == 499.90
    assert produto.tipo_validade == "VITALICIO"
    assert produto.duracao_dias is None
    assert produto.ativo is True


def test_criar_produto_temporario():
    produto = Produto(
        nome="Curso de Trading",
        categoria="Curso",
        preco=199.90,
        tipo_validade="TEMPORARIO",
        duracao_dias=365
    )

    assert produto.tipo_validade == "TEMPORARIO"
    assert produto.duracao_dias == 365


def test_produto_nao_aceita_nome_vazio():
    with pytest.raises(
        ValueError,
        match="O nome do produto é obrigatório"
    ):
        Produto(
            nome="   ",
            preco=100,
            tipo_validade="VITALICIO"
        )


def test_produto_nao_aceita_preco_negativo():
    with pytest.raises(
        ValueError,
        match="O preço do produto não pode ser negativo"
    ):
        Produto(
            nome="Produto inválido",
            preco=-10,
            tipo_validade="VITALICIO"
        )


def test_produto_nao_aceita_tipo_validade_invalido():
    with pytest.raises(
        ValueError,
        match="O tipo de validade deve ser"
    ):
        Produto(
            nome="Produto inválido",
            preco=100,
            tipo_validade="MENSAL"
        )


def test_produto_temporario_exige_duracao():
    with pytest.raises(
        ValueError,
        match="Produtos temporários devem ter duração"
    ):
        Produto(
            nome="Curso temporário",
            preco=100,
            tipo_validade="TEMPORARIO"
        )


def test_produto_vitalicio_nao_aceita_duracao():
    with pytest.raises(
        ValueError,
        match="Produtos vitalícios não devem ter duração"
    ):
        Produto(
            nome="Curso vitalício",
            preco=100,
            tipo_validade="VITALICIO",
            duracao_dias=365
        )