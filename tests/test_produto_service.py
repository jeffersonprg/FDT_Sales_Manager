import pytest

from src.models.produto import Produto
from src.services.produto_service import ProdutoService


def test_criar_e_buscar_produto(banco_temporario):
    produto = Produto(
        nome="Mentoria Premium",
        categoria="Mentoria",
        preco=499.90,
        tipo_validade="VITALICIO"
    )

    produto_id = ProdutoService.criar_produto(produto)

    produto_encontrado = ProdutoService.buscar_produto(produto_id)

    assert produto_encontrado is not None
    assert produto_encontrado.id == produto_id
    assert produto_encontrado.nome == "Mentoria Premium"
    assert produto_encontrado.preco == 499.90
    assert produto_encontrado.ativo is True


def test_buscar_produto_inexistente(banco_temporario):
    produto = ProdutoService.buscar_produto(9999)

    assert produto is None


def test_listar_produtos(banco_temporario):
    ProdutoService.criar_produto(
        Produto(
            nome="Curso Básico",
            preco=99.90,
            tipo_validade="TEMPORARIO",
            duracao_dias=180
        )
    )

    ProdutoService.criar_produto(
        Produto(
            nome="Mentoria Avançada",
            preco=599.90,
            tipo_validade="VITALICIO"
        )
    )

    produtos = ProdutoService.listar_produtos()

    assert len(produtos) == 2
    assert produtos[0].nome == "Curso Básico"
    assert produtos[1].nome == "Mentoria Avançada"


def test_atualizar_produto(banco_temporario):
    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Inicial",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=90
        )
    )

    produto = ProdutoService.buscar_produto(produto_id)

    assert produto is not None

    produto.nome = "Curso Atualizado"
    produto.preco = 149.90
    produto.duracao_dias = 180

    ProdutoService.atualizar_produto(produto)

    produto_atualizado = ProdutoService.buscar_produto(produto_id)

    assert produto_atualizado is not None
    assert produto_atualizado.nome == "Curso Atualizado"
    assert produto_atualizado.preco == 149.90
    assert produto_atualizado.duracao_dias == 180


def test_desativar_produto(banco_temporario):
    produto_id = ProdutoService.criar_produto(
        Produto(
            nome="Produto a desativar",
            preco=50,
            tipo_validade="VITALICIO"
        )
    )

    desativado = ProdutoService.desativar_produto(produto_id)
    produto = ProdutoService.buscar_produto(produto_id)

    assert desativado is True
    assert produto is not None
    assert produto.ativo is False


def test_desativar_produto_inexistente(banco_temporario):
    desativado = ProdutoService.desativar_produto(9999)

    assert desativado is False
    
def test_pesquisar_produto_por_nome(
    banco_temporario
):
    ProdutoService.criar_produto(
        Produto(
            nome="Mentoria Premium",
            categoria="Mentoria",
            preco=500,
            tipo_validade="VITALICIO"
        )
    )

    ProdutoService.criar_produto(
        Produto(
            nome="Curso Básico",
            categoria="Curso",
            preco=100,
            tipo_validade="TEMPORARIO",
            duracao_dias=90
        )
    )

    produtos = ProdutoService.pesquisar_produtos(
        "mentoria"
    )

    assert len(produtos) == 1
    assert produtos[0].nome == "Mentoria Premium"


def test_pesquisar_produto_por_categoria_e_descricao(
    banco_temporario
):
    ProdutoService.criar_produto(
        Produto(
            nome="Formação Avançada",
            categoria="Trading",
            preco=300,
            descricao="Curso sobre análise técnica",
            tipo_validade="TEMPORARIO",
            duracao_dias=180
        )
    )

    resultados_categoria = (
        ProdutoService.pesquisar_produtos("Trading")
    )

    resultados_descricao = (
        ProdutoService.pesquisar_produtos(
            "análise técnica"
        )
    )

    assert len(resultados_categoria) == 1
    assert resultados_categoria[0].nome == (
        "Formação Avançada"
    )

    assert len(resultados_descricao) == 1
    assert resultados_descricao[0].nome == (
        "Formação Avançada"
    )


def test_pesquisar_apenas_produtos_ativos(
    banco_temporario
):
    produto_ativo_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Ativo",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    produto_inativo_id = ProdutoService.criar_produto(
        Produto(
            nome="Curso Inativo",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    ProdutoService.desativar_produto(
        produto_inativo_id
    )

    produtos = ProdutoService.pesquisar_produtos(
        termo="Curso",
        apenas_ativos=True
    )

    assert len(produtos) == 1
    assert produtos[0].id == produto_ativo_id
    assert produtos[0].ativo is True


def test_pesquisa_vazia_lista_todos_os_produtos(
    banco_temporario
):
    ProdutoService.criar_produto(
        Produto(
            nome="Produto B",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    ProdutoService.criar_produto(
        Produto(
            nome="Produto A",
            preco=100,
            tipo_validade="VITALICIO"
        )
    )

    produtos = ProdutoService.pesquisar_produtos("")

    assert len(produtos) == 2
    assert produtos[0].nome == "Produto A"
    assert produtos[1].nome == "Produto B"


def test_criacao_atribui_id_ao_produto(banco_temporario):
    produto = Produto(nome="Produto com ID", preco=10)

    produto_id = ProdutoService.criar_produto(produto)

    assert produto.id == produto_id


def test_nome_produto_e_unico_sem_diferenciar_caixa(banco_temporario):
    ProdutoService.criar_produto(
        Produto(nome="Curso Premium", preco=100)
    )

    with pytest.raises(ValueError, match="este nome"):
        ProdutoService.criar_produto(
            Produto(nome="curso premium", preco=100)
        )


def test_atualizacao_revalida_produto(banco_temporario):
    produto_id = ProdutoService.criar_produto(
        Produto(nome="Produto válido", preco=10)
    )
    produto = ProdutoService.buscar_produto(produto_id)
    assert produto is not None

    produto.nome = "   "

    with pytest.raises(ValueError, match="nome do produto"):
        ProdutoService.atualizar_produto(produto)


def test_atualizar_produto_inexistente_retorna_false(banco_temporario):
    atualizado = ProdutoService.atualizar_produto(
        Produto(id=9999, nome="Inexistente", preco=10)
    )

    assert atualizado is False


def test_reativar_produto(banco_temporario):
    produto_id = ProdutoService.criar_produto(
        Produto(nome="Produto reativável", preco=10)
    )

    assert ProdutoService.desativar_produto(produto_id) is True
    assert ProdutoService.reativar_produto(produto_id) is True
    assert ProdutoService.buscar_produto(produto_id).ativo is True
