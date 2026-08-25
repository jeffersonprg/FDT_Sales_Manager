from __future__ import annotations

import base64
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.database.database import get_connection
from src.services.dashboard_service import DashboardService
from src.services.estatisticas_service import EstatisticasService
from src.services.faturacao_service import FaturacaoService
from src.services.importacao_csv_service import ImportacaoCSVService


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "data" / "reports"


class RelatorioHTMLService:
    @staticmethod
    def _formatar_moeda(valor) -> str:
        numero = float(valor or 0)
        formatado = f"{numero:,.2f}"
        return "€ " + formatado.replace(",", "X").replace(".", ",").replace(
            "X",
            ".",
        )

    @staticmethod
    def _converter_datetime(valor) -> datetime | None:
        if valor is None or valor == "":
            return None
        if isinstance(valor, datetime):
            return valor
        if isinstance(valor, date):
            return datetime.combine(valor, datetime.min.time())

        return datetime.fromisoformat(str(valor))

    @staticmethod
    def _formatar_data(valor) -> str:
        convertido = RelatorioHTMLService._converter_datetime(valor)
        return "—" if convertido is None else convertido.strftime("%d/%m/%Y")

    @staticmethod
    def _formatar_datetime(valor) -> str:
        convertido = RelatorioHTMLService._converter_datetime(valor)
        return (
            "—"
            if convertido is None
            else convertido.strftime("%d/%m/%Y %H:%M")
        )

    @staticmethod
    def _svg_base64(conteudo: str) -> str:
        return base64.b64encode(conteudo.encode("utf-8")).decode("ascii")

    @staticmethod
    def _grafico_produtos(produtos: list[dict]) -> str | None:
        if not produtos:
            return None

        selecionados = produtos[:8]
        largura = 900
        margem_esquerda = 230
        margem_direita = 140
        altura_linha = 48
        altura = 72 + len(selecionados) * altura_linha
        area = largura - margem_esquerda - margem_direita
        maior_valor = max(item["faturacao_total"] for item in selecionados) or 1
        elementos = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" role="img" aria-label="Faturação por produto">',
            '<rect width="100%" height="100%" fill="white"/>',
            '<text x="20" y="30" font-family="system-ui" font-size="19" font-weight="700" fill="#0f172a">Faturação por produto</text>',
        ]

        for indice, item in enumerate(selecionados):
            y = 58 + indice * altura_linha
            largura_barra = area * item["faturacao_total"] / maior_valor
            nome = escape(str(item["produto_nome"]))
            valor = escape(
                RelatorioHTMLService._formatar_moeda(
                    item["faturacao_total"]
                )
            )
            elementos.extend([
                f'<text x="20" y="{y + 20}" font-family="system-ui" font-size="13" fill="#334155">{nome}</text>',
                f'<rect x="{margem_esquerda}" y="{y}" width="{area}" height="28" rx="6" fill="#eff6ff"/>',
                f'<rect x="{margem_esquerda}" y="{y}" width="{largura_barra:.1f}" height="28" rx="6" fill="#2563eb"/>',
                f'<text x="{margem_esquerda + area + 10}" y="{y + 19}" font-family="system-ui" font-size="12" font-weight="700" fill="#1e3a8a">{valor}</text>',
            ])

        elementos.append("</svg>")
        return RelatorioHTMLService._svg_base64("".join(elementos))

    @staticmethod
    def _grafico_mensal(meses: list[dict]) -> str | None:
        if not meses:
            return None

        largura = 900
        altura = 430
        esquerda, direita, topo, base = 70, 30, 65, 65
        area_x = largura - esquerda - direita
        area_y = altura - topo - base
        valores = [item["faturacao_total"] for item in meses]
        maior_valor = max(valores) or 1
        divisor = max(len(meses) - 1, 1)
        pontos = []

        for indice, item in enumerate(meses):
            x = esquerda + area_x * indice / divisor
            y = topo + area_y * (1 - item["faturacao_total"] / maior_valor)
            pontos.append((x, y, item))

        elementos = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" role="img" aria-label="Evolução mensal da faturação">',
            '<rect width="100%" height="100%" fill="white"/>',
            '<text x="20" y="30" font-family="system-ui" font-size="19" font-weight="700" fill="#0f172a">Evolução mensal da faturação</text>',
        ]

        for fracao in (0, 0.25, 0.5, 0.75, 1):
            y = topo + area_y * (1 - fracao)
            valor = RelatorioHTMLService._formatar_moeda(maior_valor * fracao)
            elementos.extend([
                f'<line x1="{esquerda}" y1="{y:.1f}" x2="{largura - direita}" y2="{y:.1f}" stroke="#e2e8f0"/>',
                f'<text x="{esquerda - 8}" y="{y + 4:.1f}" text-anchor="end" font-family="system-ui" font-size="10" fill="#64748b">{escape(valor)}</text>',
            ])

        if len(pontos) == 1:
            x, y, _ = pontos[0]
            pontos[0] = (esquerda + area_x / 2, y, pontos[0][2])

        coordenadas = " ".join(
            f"{x:.1f},{y:.1f}" for x, y, _ in pontos
        )
        elementos.append(
            f'<polyline points="{coordenadas}" fill="none" stroke="#0f766e" stroke-width="4" stroke-linejoin="round"/>'
        )

        for x, y, item in pontos:
            elementos.extend([
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#0f766e" stroke="white" stroke-width="3"/>',
                f'<text x="{x:.1f}" y="{altura - 28}" text-anchor="middle" font-family="system-ui" font-size="11" fill="#475569">{escape(item["mes"])}</text>',
            ])

        elementos.append("</svg>")
        return RelatorioHTMLService._svg_base64("".join(elementos))

    @staticmethod
    def _listar_pedidos_relatorio(
        data_inicio: date | datetime | None,
        data_fim: date | datetime | None,
        limite: int,
    ) -> list[dict]:
        inicio, fim = FaturacaoService._normalizar_periodo(
            data_inicio,
            data_fim,
        )
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT
                    pedidos.id,
                    pedidos.referencia_externa,
                    clientes.nome AS cliente_nome,
                    pedidos.pago_em,
                    pedidos.total,
                    COUNT(itens_pedido.id) AS total_itens
                FROM pedidos
                INNER JOIN clientes ON clientes.id = pedidos.cliente_id
                INNER JOIN itens_pedido ON itens_pedido.pedido_id = pedidos.id
                WHERE pedidos.estado = 'PAGO'
                  AND (? IS NULL OR DATE(pedidos.pago_em) >= ?)
                  AND (? IS NULL OR DATE(pedidos.pago_em) <= ?)
                GROUP BY
                    pedidos.id,
                    pedidos.referencia_externa,
                    clientes.nome,
                    pedidos.pago_em,
                    pedidos.total
                ORDER BY pedidos.pago_em DESC, pedidos.id DESC
                LIMIT ?
            """, (inicio, inicio, fim, fim, limite)).fetchall()

            return [dict(row) for row in rows]
        finally:
            connection.close()

    @staticmethod
    def gerar(
        caminho_saida: str | Path | None = None,
        data_inicio: date | datetime | None = None,
        data_fim: date | datetime | None = None,
        titulo: str = "Relatório Comercial",
        limite_pedidos: int = 20,
        limite_importacoes: int = 10,
    ) -> Path:
        if limite_pedidos <= 0:
            raise ValueError("O limite de pedidos deve ser superior a zero.")
        if limite_importacoes <= 0:
            raise ValueError("O limite de importações deve ser superior a zero.")

        inicio, fim = FaturacaoService._normalizar_periodo(
            data_inicio,
            data_fim,
        )
        gerado_em = datetime.now(timezone.utc).replace(tzinfo=None)

        if caminho_saida is None:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            caminho = REPORTS_DIR / (
                "relatorio_comercial_"
                + gerado_em.strftime("%Y%m%d_%H%M%S")
                + ".html"
            )
        else:
            caminho = Path(caminho_saida).expanduser().resolve()
            if caminho.suffix.lower() != ".html":
                raise ValueError("O relatório deve possuir extensão .html.")
            caminho.parent.mkdir(parents=True, exist_ok=True)

        dashboard = DashboardService.obter_resumo()
        faturacao = FaturacaoService.obter_resumo(data_inicio, data_fim)
        estatisticas = EstatisticasService.obter_resumo_vendas(
            data_inicio,
            data_fim,
        )
        produtos = EstatisticasService.vendas_por_produto(
            data_inicio,
            data_fim,
        )
        meses = EstatisticasService.faturacao_por_mes(data_inicio, data_fim)
        pedidos = RelatorioHTMLService._listar_pedidos_relatorio(
            data_inicio,
            data_fim,
            limite_pedidos,
        )
        importacoes = ImportacaoCSVService.listar_historico(
            limite_importacoes
        )

        ambiente = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(("html", "xml")),
        )
        ambiente.filters["moeda"] = RelatorioHTMLService._formatar_moeda
        ambiente.filters["data"] = RelatorioHTMLService._formatar_data
        ambiente.filters["datahora"] = (
            RelatorioHTMLService._formatar_datetime
        )
        template = ambiente.get_template("relatorio_comercial.html")
        conteudo = template.render(
            titulo=titulo.strip() or "Relatório Comercial",
            gerado_em=gerado_em,
            periodo_inicio=inicio,
            periodo_fim=fim,
            dashboard=dashboard,
            faturacao=faturacao,
            estatisticas=estatisticas,
            produtos=produtos,
            meses=meses,
            pedidos=pedidos,
            importacoes=importacoes,
            grafico_produtos=RelatorioHTMLService._grafico_produtos(produtos),
            grafico_mensal=RelatorioHTMLService._grafico_mensal(meses),
        )

        caminho_temporario = caminho.with_suffix(".tmp")
        caminho_temporario.write_text(conteudo, encoding="utf-8")
        caminho_temporario.replace(caminho)

        return caminho
