from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

from src.database.database import get_connection
from src.services.importacao_csv_service import (
    ErroImportacaoCSV,
    ImportacaoCSVService,
)


CABECALHO = (
    "data,nome_cliente,morada,informacao_cliente,pedido,produto,"
    "quantidade,preco_unitario,faturacao\n"
)


@pytest.fixture
def fabrica_csv():
    pasta = Path(__file__).resolve().parent / "_temp_csv"
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = []

    def criar(conteudo: str) -> Path:
        caminho = pasta / f"importacao_{uuid4().hex}.csv"
        caminho.write_text(conteudo, encoding="utf-8")
        caminhos.append(caminho)
        return caminho

    yield criar

    for caminho in caminhos:
        caminho.unlink(missing_ok=True)


def test_importar_csv_exemplo_para_minicrm(banco_temporario):
    caminho = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "data"
        / "imports"
        / "vendas_exemplo.csv"
    )

    resumo = ImportacaoCSVService.importar(caminho)

    assert resumo.linhas_lidas == 5
    assert resumo.clientes_criados == 4
    assert resumo.clientes_reutilizados == 1
    assert resumo.produtos_criados == 2
    assert resumo.produtos_reutilizados == 3
    assert resumo.pedidos_criados == 5
    assert resumo.itens_criados == 5
    assert resumo.faturacao_importada == 2696.0

    connection = get_connection()
    try:
        estados = connection.execute(
            "SELECT DISTINCT estado FROM pedidos"
        ).fetchall()
        acessos = connection.execute("""
            SELECT inicio_acesso, fim_acesso
            FROM itens_pedido
            ORDER BY id
        """).fetchall()
    finally:
        connection.close()

    assert [row["estado"] for row in estados] == ["PAGO"]
    assert acessos[0]["inicio_acesso"] == "2026-07-15"
    assert acessos[0]["fim_acesso"] is None


def test_mesmo_arquivo_nao_e_processado_duas_vezes(banco_temporario):
    caminho = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "data"
        / "imports"
        / "vendas_exemplo.csv"
    )

    ImportacaoCSVService.importar(caminho)
    segundo = ImportacaoCSVService.importar(caminho)

    assert segundo.arquivo_ja_importado is True
    assert segundo.pedidos_criados == 0

    connection = get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) AS total FROM pedidos"
        ).fetchone()["total"]
    finally:
        connection.close()

    assert total == 5

    historico = ImportacaoCSVService.listar_historico()
    assert len(historico) == 1
    assert historico[0]["nome_arquivo"] == "vendas_exemplo.csv"
    assert historico[0]["faturacao_importada"] == 2696.0


def test_referencias_existentes_sao_ignoradas_em_outro_arquivo(
    banco_temporario,
    fabrica_csv
):
    original = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "data"
        / "imports"
        / "vendas_exemplo.csv"
    )
    ImportacaoCSVService.importar(original)
    copia_modificada = fabrica_csv(
        original.read_text(encoding="utf-8") + "\n"
    )

    resumo = ImportacaoCSVService.importar(copia_modificada)

    assert resumo.pedidos_criados == 0
    assert resumo.pedidos_ignorados == 5
    assert resumo.referencias_ignoradas == [
        "PED-001",
        "PED-002",
        "PED-003",
        "PED-004",
        "PED-005",
    ]


def test_multiplas_linhas_formam_um_pedido_e_agregam_produto(
    banco_temporario,
    fabrica_csv
):
    caminho = fabrica_csv(
        CABECALHO
        + "2026-08-01,Ana,Rua A,Cliente,PED-MULTI,Curso A,1,100,100\n"
        + "2026-08-01,Ana,Rua A,Cliente,PED-MULTI,Curso A,2,100,200\n"
        + "2026-08-01,Ana,Rua A,Cliente,PED-MULTI,Curso B,1,50,50\n"
    )

    resumo = ImportacaoCSVService.importar(caminho)

    assert resumo.pedidos_criados == 1
    assert resumo.itens_criados == 2
    assert resumo.faturacao_importada == 350.0

    connection = get_connection()
    try:
        pedido = connection.execute(
            "SELECT total FROM pedidos"
        ).fetchone()
        quantidades = [
            row["quantidade"]
            for row in connection.execute(
                "SELECT quantidade FROM itens_pedido ORDER BY quantidade DESC"
            ).fetchall()
        ]
    finally:
        connection.close()

    assert pedido["total"] == 350.0
    assert quantidades == [3, 1]


def test_faturacao_inconsistente_nao_grava_dados(
    banco_temporario,
    fabrica_csv
):
    caminho = fabrica_csv(
        CABECALHO
        + "2026-08-01,Ana,Rua A,Cliente,PED-OK,Curso A,1,100,100\n"
        + "2026-08-02,Bia,Rua B,Cliente,PED-ERRO,Curso B,2,50,80\n"
    )

    with pytest.raises(ErroImportacaoCSV, match="Faturação inconsistente"):
        ImportacaoCSVService.importar(caminho)

    connection = get_connection()
    try:
        pedidos = connection.execute(
            "SELECT COUNT(*) AS total FROM pedidos"
        ).fetchone()["total"]
        importacoes = connection.execute(
            "SELECT COUNT(*) AS total FROM importacoes_csv"
        ).fetchone()["total"]
    finally:
        connection.close()

    assert pedidos == 0
    assert importacoes == 0


def test_pedido_com_cliente_inconsistente_faz_rollback(
    banco_temporario,
    fabrica_csv
):
    caminho = fabrica_csv(
        CABECALHO
        + "2026-08-01,Ana,Rua A,Cliente,PED-001,Curso A,1,100,100\n"
        + "2026-08-01,Bia,Rua B,Cliente,PED-001,Curso B,1,50,50\n"
    )

    with pytest.raises(ErroImportacaoCSV, match="dados inconsistentes"):
        ImportacaoCSVService.importar(caminho)

    connection = get_connection()
    try:
        clientes = connection.execute(
            "SELECT COUNT(*) AS total FROM clientes"
        ).fetchone()["total"]
    finally:
        connection.close()

    assert clientes == 0


def test_produto_temporario_importado_recebe_validade(
    banco_temporario,
    fabrica_csv
):
    caminho = fabrica_csv(
        CABECALHO
        + "2026-08-01,Ana,Rua A,Cliente,PED-TEMP,Curso,1,100,100\n"
    )

    ImportacaoCSVService.importar(
        caminho,
        tipo_validade_padrao="TEMPORARIO",
        duracao_dias_padrao=10,
    )

    connection = get_connection()
    try:
        item = connection.execute(
            "SELECT inicio_acesso, fim_acesso FROM itens_pedido"
        ).fetchone()
    finally:
        connection.close()

    assert item["inicio_acesso"] == date(2026, 8, 1).isoformat()
    assert item["fim_acesso"] == date(2026, 8, 10).isoformat()


def test_coluna_obrigatoria_em_falta_e_reportada(
    banco_temporario,
    fabrica_csv
):
    caminho = fabrica_csv(
        "data,nome_cliente,pedido,produto,quantidade,preco_unitario,faturacao\n"
        "2026-08-01,Ana,PED-001,Curso,1,100,100\n"
    )

    with pytest.raises(ErroImportacaoCSV, match="morada"):
        ImportacaoCSVService.importar(caminho)
