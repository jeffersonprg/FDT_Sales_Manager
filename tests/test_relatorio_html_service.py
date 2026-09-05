import base64
from datetime import date
from pathlib import Path
import re
from uuid import uuid4

import pytest

from src.services.importacao_csv_service import ImportacaoCSVService
from src.services.relatorio_html_service import RelatorioHTMLService
from src.i18n import set_language


@pytest.fixture
def caminho_relatorio():
    pasta = Path(__file__).resolve().parent / "_temp_reports"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"relatorio_{uuid4().hex}.html"

    yield caminho

    caminho.unlink(missing_ok=True)
    caminho.with_suffix(".tmp").unlink(missing_ok=True)


def importar_exemplo() -> None:
    caminho_csv = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "data"
        / "imports"
        / "vendas_exemplo.csv"
    )
    ImportacaoCSVService.importar(caminho_csv)


def test_gerar_relatorio_com_dados(
    banco_temporario,
    caminho_relatorio
):
    importar_exemplo()

    resultado = RelatorioHTMLService.gerar(
        caminho_saida=caminho_relatorio,
        titulo="Relatório de Teste",
    )
    conteudo = resultado.read_text(encoding="utf-8")

    assert resultado == caminho_relatorio.resolve()
    assert "Relatório de Teste" in conteudo
    assert "€ 2.696,00" in conteudo
    assert "Curso Python" in conteudo
    assert "PED-005" in conteudo
    assert "vendas_exemplo.csv" in conteudo
    assert conteudo.count("data:image/svg+xml;base64,") == 2
    assert conteudo.count("data:image/png;base64,") == 2
    assert 'class="brand-logo"' in conteudo
    assert 'rel="icon"' in conteudo
    assert "TSS Invest" in conteudo
    assert "TS Invest —" not in conteudo
    assert not caminho_relatorio.with_suffix(".tmp").exists()


def test_relatorio_vazio_apresenta_mensagens(
    banco_temporario,
    caminho_relatorio
):
    RelatorioHTMLService.gerar(caminho_saida=caminho_relatorio)
    conteudo = caminho_relatorio.read_text(encoding="utf-8")

    assert "Ainda não existem vendas pagas" in conteudo
    assert "Nenhum pedido faturado" in conteudo
    assert "Nenhum arquivo CSV foi importado" in conteudo
    assert "data:image/svg+xml;base64," not in conteudo
    assert conteudo.count("data:image/png;base64,") == 2


def test_relatorio_filtra_periodo(
    banco_temporario,
    caminho_relatorio
):
    importar_exemplo()

    RelatorioHTMLService.gerar(
        caminho_saida=caminho_relatorio,
        data_inicio=date(2026, 7, 16),
        data_fim=date(2026, 7, 17),
    )
    conteudo = caminho_relatorio.read_text(encoding="utf-8")

    assert "€ 1.098,00" in conteudo
    assert "PED-002" in conteudo
    assert "PED-003" in conteudo
    assert "PED-001" not in conteudo


def test_relatorio_escapa_titulo_html(
    banco_temporario,
    caminho_relatorio
):
    RelatorioHTMLService.gerar(
        caminho_saida=caminho_relatorio,
        titulo="<script>alert('x')</script>",
    )
    conteudo = caminho_relatorio.read_text(encoding="utf-8")

    assert "<script>alert" not in conteudo
    assert "&lt;script&gt;" in conteudo


def test_relatorio_rejeita_extensao_e_periodo_invalidos(
    banco_temporario,
    caminho_relatorio
):
    with pytest.raises(ValueError, match="extensão .html"):
        RelatorioHTMLService.gerar(caminho_relatorio.with_suffix(".txt"))

    with pytest.raises(ValueError, match="data inicial"):
        RelatorioHTMLService.gerar(
            caminho_relatorio,
            data_inicio=date(2026, 8, 2),
            data_fim=date(2026, 8, 1),
        )


def test_relatorio_em_ingles(
    banco_temporario,
    caminho_relatorio,
):
    RelatorioHTMLService.gerar(
        caminho_saida=caminho_relatorio,
        idioma="en",
    )
    conteudo = caminho_relatorio.read_text(encoding="utf-8")

    assert '<html lang="en">' in conteudo
    assert "Sales Report" in conteudo
    assert "Overview" in conteudo
    assert "There are no paid sales in the period yet." in conteudo
    assert "No invoiced orders in the selected period." in conteudo
    assert "Visão geral" not in conteudo


def test_relatorio_usa_espanhol_selecionado_incluindo_graficos(
    banco_temporario,
    caminho_relatorio,
):
    importar_exemplo()
    try:
        set_language("es")
        RelatorioHTMLService.gerar(caminho_saida=caminho_relatorio)
    finally:
        set_language("pt")
    conteudo = caminho_relatorio.read_text(encoding="utf-8")

    assert '<html lang="es">' in conteudo
    assert "Informe comercial" in conteudo
    assert "Resumen general" in conteudo
    assert "Pedidos facturados recientes" in conteudo
    assert "Historial de importaciones CSV" in conteudo
    assert '<span class="pill">Pagado</span>' in conteudo
    grafico = re.search(
        r'data:image/svg\+xml;base64,([^"\s]+)', conteudo,
    )
    assert grafico is not None
    svg = base64.b64decode(grafico.group(1)).decode("utf-8")
    assert "Facturación por producto" in svg
